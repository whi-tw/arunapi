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
		userGroup := v1.Group("next_collection")
		{
			user := new(controllers.NextRefuseCollectionController)
			userGroup.GET("/:postcode", user.Retrieve)
		}
	}
	return router

}
