package config

import (
	"encoding/json"
	"fmt"
	"os"
)

type LLMConfig struct {
	ModelName string `json:"model_name"`
}

type DbConfig struct {
	Port                    string   `json:"apiPort"`
	DbPath                  string   `json:"dbPath"`
	DbLogPath               string   `json:"dbLogPath"`
	LogPath                 string   `json:"logPath"`
	TgCloud                 bool     `json:"tgCloud"`
	ConversationAccessRoles []string `json:"conversationAccessRoles"`
	TgDbHost                string   `json:"hostname"`
	Username                string   `json:"username"`
	Password                string   `json:"password"`
	// GetToken string `json:"getToken"`
	// DefaultTimeout       string `json:"default_timeout"`
	// DefaultMemThreshold string `json:"default_mem_threshold"`
	// DefaultThreadLimit  string `json:"default_thread_limit"`
}

type Config struct {
	DbConfig
	// LLMConfig
}

func LoadConfig(paths ...string) (Config, error) {
	var cfg Config
	for _, path := range paths {
		var b []byte
		if _, err := os.Stat(path); os.IsNotExist(err) {
			// file doesn't exist read from env
			cfg := os.Getenv("CONFIG_FILES")
			if cfg == "" {
				fmt.Println("CONFIG path is not found nor is the CONFIG json env variable defined")
				os.Exit(1)
			}
			b = []byte(cfg)
		} else {
			b, err = os.ReadFile(path)
			if err != nil {
				return Config{}, err
			}
		}

		if err := json.Unmarshal(b, &cfg); err != nil {
			return Config{}, err
		}
	}
	return cfg, nil
}
