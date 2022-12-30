package cmd

import (
	"github.com/spf13/cobra"
	"github.com/spf13/viper"
	"github.com/whi-tw/arunapi/server"
	"log"
)

var (
	environment string
	cfgFile     string

	rootCmd = &cobra.Command{
		Use:   "arunapi",
		Short: "API for Arun DC Services",
		Long:  `API server for accessing Arun District Council Services`,
		Run: func(cmd *cobra.Command, args []string) {
			server.Init()
		},
	}
)

func Execute(version string) error {
	rootCmd.Version = version
	return rootCmd.Execute()
}

func init() {
	cobra.OnInitialize(initConfig)

	rootCmd.PersistentFlags().StringVar(&cfgFile, "config", "", "config file (default \".arunapi.yaml\")")
	rootCmd.PersistentFlags().String("listenAddress", ":8080", "listen address")

}

func initConfig() {
	if cfgFile != "" {
		viper.SetConfigFile(cfgFile)
	} else {
		viper.AddConfigPath(".")
		viper.SetConfigType("yaml")
		viper.SetConfigName("arunapi")
	}
	viper.AutomaticEnv()

	if err := viper.ReadInConfig(); err != nil {
		if _, ok := err.(viper.ConfigFileNotFoundError); ok {
			log.Println("Config file not found; using envars and defaults")
		} else {
			cobra.CheckErr(err)
		}
	}
}
