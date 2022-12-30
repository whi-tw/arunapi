package controllers

import (
	"github.com/gin-gonic/gin"
	"github.com/whi-tw/arunapi/models"
	"net/http"
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
