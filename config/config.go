package config

import (
	"github.com/spf13/viper"
	"log"
)

var config *Config

type Config struct {
	Port string `mapstructure:"port"`
}

func LoadConfig(environment string) error {
	viper.SetDefault("port", "8080")
	viper.AddConfigPath(".")
	viper.SetConfigName(environment)
	viper.SetConfigType("yaml")

	viper.AutomaticEnv()

	if err := viper.ReadInConfig(); err != nil {
		if _, ok := err.(viper.ConfigFileNotFoundError); ok {
			log.Println("Config file not found; using envars and defaults")
		} else {
			log.Fatal(err)
		}
	}
	err := viper.Unmarshal(&config)
	return err
}

func GetConfig() *Config {
	return config
}
