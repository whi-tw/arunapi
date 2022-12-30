package controllers

import (
	"github.com/gin-gonic/gin"
	"github.com/whi-tw/arunapi/models"
	"net/http"
	"strconv"
	"time"
)

type NextRefuseCollectionController struct{}

var nextRefuseCollectionModel = new(models.NextRefuseCollection)

func (u NextRefuseCollectionController) Retrieve(c *gin.Context) {
	if c.Param("postcode") != "" {
		postcode := c.Param("postcode")
		nextCollection, err := nextRefuseCollectionModel.GetCollectionForPostcode(c, postcode)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"message": "Error retrieving next collection", "error": err})
			c.Abort()
			return
		}
		c.JSON(http.StatusOK, nextCollection)
		return
	}
	c.JSON(http.StatusBadRequest, gin.H{"message": "bad request"})
	c.Abort()
	return
}

func (u NextRefuseCollectionController) Calendar(c *gin.Context) {
	if c.Param("postcode") != "" {
		postcode := c.Param("postcode")
		transparentEvents, err := strconv.ParseBool(c.DefaultQuery("transparent", "true"))
		if err != nil {
			transparentEvents = true
		}
		var todoTime *time.Time
		tt, err := time.Parse("15:04", c.DefaultQuery("todo_time", "19:00"))
		if err != nil {
			todoTime = nil
		} else {
			todoTime = &tt
		}
		collectionCalendar, err := nextRefuseCollectionModel.GetCollectionCalendarForPostcode(c, postcode, transparentEvents, todoTime)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"message": "Error generating collection calendar", "error": err})
			c.Abort()
			return
		}
		c.String(http.StatusOK, collectionCalendar)
		c.Writer.Header().Set("Content-Type", "text/calendar")
		return
	}
	c.JSON(http.StatusBadRequest, gin.H{"message": "bad request"})
	c.Abort()
	return
}
