package cmd

import (
	"fmt"
	"github.com/spf13/cobra"
	"github.com/spf13/pflag"
	"github.com/spf13/viper"
	"github.com/whi-tw/arunapi/server"
	"strings"
)

var (
	cfgFile       string
	listenAddress string
	ginMode       string

	replaceHyphenWithCamelCase = false

	rootCmd = &cobra.Command{
		Use:   "arunapi",
		Short: "API for Arun DC Services",
		Long:  `API server for accessing Arun District Council Services`,
		PersistentPreRunE: func(cmd *cobra.Command, args []string) error {
			return initConfig(cmd)
		},
		Run: func(cmd *cobra.Command, args []string) {
			server.Init(listenAddress, ginMode)
		},
	}
)

func Execute(version string) error {
	rootCmd.Version = version
	return rootCmd.Execute()
}

func init() {
	rootCmd.Flags().StringVar(&cfgFile, "config-file", "", "config file (default \".arunapi.yaml\")")
	rootCmd.Flags().StringVar(&listenAddress, "listen-address", ":8080", "listen address")
	rootCmd.Flags().StringVar(&ginMode, "mode", "release", "mode to run in (debug/release)")
}

func initConfig(cmd *cobra.Command) error {
	v := viper.New()
	if cfgFile != "" {
		v.SetConfigFile(cfgFile)
	} else {
		v.AddConfigPath(".")
		v.SetConfigType("yaml")
		v.SetConfigName("arunapi")
	}

	if err := v.ReadInConfig(); err != nil {
		// It's okay if there isn't a config file
		if _, ok := err.(viper.ConfigFileNotFoundError); !ok {
			return err
		}
	}
	v.SetEnvKeyReplacer(strings.NewReplacer("-", "_"))
	v.AutomaticEnv()
	bindFlags(cmd, v)

	return nil
}

func bindFlags(cmd *cobra.Command, v *viper.Viper) {
	cmd.Flags().VisitAll(func(f *pflag.Flag) {
		// Determine the naming convention of the flags when represented in the config file
		configName := f.Name
		// If using camelCase in the config file, replace hyphens with a camelCased string.
		// Since viper does case-insensitive comparisons, we don't need to bother fixing the case, and only need to remove the hyphens.
		if replaceHyphenWithCamelCase {
			configName = strings.ReplaceAll(f.Name, "-", "")
		}

		// Apply the viper config value to the flag when the flag is not set and viper has a value
		if !f.Changed && v.IsSet(configName) {
			val := v.Get(configName)
			cmd.Flags().Set(f.Name, fmt.Sprintf("%v", val))
		}
	})
}
