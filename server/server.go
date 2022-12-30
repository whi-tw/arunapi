package server

import (
	"github.com/gin-gonic/gin"
)

func Init(listenAddress string, mode string) {
	r := NewRouter()
	gin.SetMode(mode)
	_ = r.Run(listenAddress)
}
