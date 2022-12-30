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
	ics "github.com/arran4/golang-ical"
	"github.com/google/uuid"
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

func (r *NextRefuseCollection) GetCollectionCalendarForPostcode(ctx context.Context, postcode string, transparentEvents bool, todoTime *time.Time) (string, error) {
	nextCollectionData, err := r.GetCollectionForPostcode(ctx, postcode)
	if err != nil {
		return "", fmt.Errorf("error getting next collection: %v", err)
	}

	cal := ics.NewCalendar()
	cal.SetProductId("arunapi")
	cal.SetMethod(ics.MethodPublish)
	cal.SetName(fmt.Sprintf("Refuse Collection for %s", postcode))
	cal.SetDescription(fmt.Sprintf("Arun District Council Refuse Collection for %s", postcode))
	if nextCollectionData.NextRubbish != nil {
		cal.AddVEvent(createCalendarEventForCollectionDate(nextCollectionData.NextRubbish, "Rubbish", transparentEvents))
	}
	if nextCollectionData.NextRecycling != nil {
		cal.AddVEvent(createCalendarEventForCollectionDate(nextCollectionData.NextRecycling, "Recycling", transparentEvents))
	}
	if nextCollectionData.NextFoodWaste != nil {
		cal.AddVEvent(createCalendarEventForCollectionDate(nextCollectionData.NextFoodWaste, "Food Waste", transparentEvents))
	}
	return cal.Serialize(), nil
}

func createCalendarEventForCollectionDate(collectionDate *CollectionDate, collectionType string, transparent bool) *ics.VEvent {
	icalDateFormatLocal := "20060102"

	event := ics.NewEvent(uuid.NewString())
	event.SetCreatedTime(time.Now())
	event.SetDtStampTime(time.Now())
	event.SetModifiedAt(time.Now())
	event.SetProperty("DTSTART;VALUE=DATE", collectionDate.Time.Format(icalDateFormatLocal))
	if transparent {
		event.SetTimeTransparency(ics.TransparencyTransparent)
	} else {
		event.SetTimeTransparency(ics.TransparencyOpaque)
	}
	event.SetSummary(fmt.Sprintf("%s Collection", collectionType))
	event.SetDescription(fmt.Sprintf("%s Collection", collectionType))
	return event
}

func createTodoItemForCollection(collectionDate *CollectionDate, todoTime *time.Time, collectionType string) *ics.VTodo {
	icalTimestampFormatUtc := "20060102T150405Z"
	//icalDateFormatUtc := "20060102Z"
	todoStartTime := collectionDate.Time.AddDate(0, 0, -1)
	todoDueTime := time.Date(todoStartTime.Year(), todoStartTime.Month(), todoStartTime.Day(), todoTime.Hour(), todoTime.Minute(), 0, 0, time.UTC)
	todo := ics.VTodo{}
	todo.SetProperty("UID", uuid.NewString())
	todo.SetProperty("DTSTAMP", time.Now().Format(icalTimestampFormatUtc))
	todo.SetProperty("DTSTART", todoStartTime.Format(icalTimestampFormatUtc))
	todo.SetProperty("DUE", todoDueTime.Format(icalTimestampFormatUtc))
	todo.SetProperty("SUMMARY", fmt.Sprintf("Take out %s bin", collectionType))
	todo.SetProperty("STATUS", "NEEDS-ACTION")
	return &todo
}
