package models

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"net/url"
	"strings"
	"time"

	"github.com/PuerkitoBio/goquery"
)

type NextRefuseCollection struct {
	CollectionDay string          `json:"collection_day"`
	NextRubbish   *CollectionDate `json:"next_rubbish"`
	NextRecycling *CollectionDate `json:"next_recycling"`
	NextFoodWaste *CollectionDate `json:"next_food_waste"`
}

type formData struct {
	Method string
	Action string
	Fields url.Values
}

func (r *NextRefuseCollection) GetCollectionForPostcode(ctx context.Context, postcode string) (*NextRefuseCollection, error) {
	res, err := http.Get("https://www1.arun.gov.uk/external/Cleansing_GDS_CollectionsSchedule.ofml")
	if err != nil {
		return nil, fmt.Errorf("error initiating refuse session: %v", err)
	}
	doc, err := goquery.NewDocumentFromReader(res.Body)
	if err != nil {
		return nil, fmt.Errorf("error parsing collection form: %v", err)
	}
	forms := doc.Find("form")
	data := formData{
		Method: forms.First().AttrOr("method", "GET"),
		Action: forms.First().AttrOr("action", ""),
		Fields: url.Values{},
	}
	forms.First().Find("input").Each(func(i int, s *goquery.Selection) {
		name, _ := s.Attr("name")
		if name != "" {
			data.Fields.Add(name, s.AttrOr("value", ""))
		}
	})
	res, err = http.PostForm(data.Action, data.Fields)
	if err != nil {
		return nil, fmt.Errorf("error loading postcode form: %v", err)
	}
	doc, err = goquery.NewDocumentFromReader(res.Body)
	if err != nil {
		return nil, fmt.Errorf("error parsing postcode form: %v", err)
	}
	forms = doc.Find("form")
	data = formData{
		Method: forms.First().AttrOr("method", "GET"),
		Action: forms.First().AttrOr("action", ""),
		Fields: url.Values{},
	}
	forms.First().Find("input").Each(func(i int, s *goquery.Selection) {
		name, _ := s.Attr("name")
		if name != "" {
			data.Fields.Add(name, s.AttrOr("value", ""))
		}
	})
	data.Fields.Set("F_Postcodesearch", postcode)

	res, err = http.PostForm(data.Action, data.Fields)
	if err != nil {
		return nil, fmt.Errorf("error submitting postcode form: %v", err)
	}
	doc, err = goquery.NewDocumentFromReader(res.Body)
	if err != nil {
		return nil, fmt.Errorf("error parsing address selection form: %v", err)
	}
	forms = doc.Find("form")
	data = formData{
		Method: forms.First().AttrOr("method", "GET"),
		Action: forms.First().AttrOr("action", ""),
		Fields: url.Values{},
	}
	forms.First().Find("input").Each(func(i int, s *goquery.Selection) {
		name, _ := s.Attr("name")
		if name != "" {
			data.Fields.Add(name, s.AttrOr("value", ""))
		}
	})
	data.Fields.Set("BB_0", "1")
	data.Fields.Del("BB_Cancel")

	res, err = http.PostForm(data.Action, data.Fields)
	if err != nil {
		return nil, fmt.Errorf("error submitting postcode form: %v", err)
	}

	doc, err = goquery.NewDocumentFromReader(res.Body)
	if err != nil {
		return nil, fmt.Errorf("error parsing collection details page: %v", err)
	}
	nextCollection := &NextRefuseCollection{}
	resultDiv := doc.Find("div.dlgmsg").First()
	if strings.Contains(resultDiv.Text(), "Your collections") {
		resultDiv.Contents().Each(func(i int, s *goquery.Selection) {
			if !s.Is("br") {
				trimmed := strings.TrimSpace(s.Text())
				if strings.Contains(trimmed, "are on a") {
					nextCollection.CollectionDay = strings.ReplaceAll(
						trimmed[strings.LastIndex(trimmed, " ")+1:], ".", "")
				} else if strings.Contains(trimmed, "is due to be collected") {
					if strings.Contains(trimmed, "rubbish") {
						collectionDate, err := getCollectionDateFromResponseLine(trimmed)
						if err != nil {
							return
						}
						nextCollection.NextRubbish = &collectionDate
					} else if strings.Contains(trimmed, "recycling") {
						collectionDate, err := getCollectionDateFromResponseLine(trimmed)
						if err != nil {
							return
						}
						nextCollection.NextRecycling = &collectionDate
					} else if strings.Contains(trimmed, "food waste") {
						collectionDate, err := getCollectionDateFromResponseLine(trimmed)
						if err != nil {
							return
						}
						nextCollection.NextFoodWaste = &collectionDate
					}
				}
			}
		})
	} else {
		return nil, fmt.Errorf("no collections found")
	}
	return nextCollection, nil
}

func getCollectionDateFromResponseLine(trimmed string) (CollectionDate, error) {
	responseDateLine := trimmed[strings.LastIndex(trimmed, " ")+1:]
	collectionTime, err := time.Parse("02/01/2006", responseDateLine)
	if err != nil {
		log.Printf("error parsing date: %v", err)

		return CollectionDate{}, err
	}
	return CollectionDate{collectionTime}, nil
}
