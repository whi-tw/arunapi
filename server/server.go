package server

import (
	"fmt"
	"github.com/whi-tw/arunapi/config"
)

func Init() {
	cfg := config.GetConfig()
	r := NewRouter()
	_ = r.Run(fmt.Sprintf(":%s", cfg.Port))
}
