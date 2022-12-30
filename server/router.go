package server

import (
	"github.com/gin-gonic/gin"
	"github.com/whi-tw/arunapi/controllers"
)

func NewRouter() *gin.Engine {
	router := gin.New()
	router.Use(gin.Logger())
	router.Use(gin.Recovery())

	health := new(controllers.HealthController)

	router.GET("/health", health.Status)
	v1 := router.Group("refuse")
	{
		nextCollectionGroup := v1.Group("next_collection")
		{
			nextCollectionController := new(controllers.NextRefuseCollectionController)
			nextCollectionGroup.GET("/:postcode", nextCollectionController.Retrieve)
			nextCollectionGroup.GET("/:postcode/calendar", nextCollectionController.Calendar)
			nextCollectionGroup.GET("/:postcode/calendar.ics", nextCollectionController.Calendar)
		}
	}
	return router

}
