# Repository Context Group: pkg_bot-rw_i18n
# Source Repository: discohook/discohook

### File: `packages/bot-rw/src/i18n/README.md`
```md
# Contributing translations to Discohook

Hello. If you would like to help translate Discohook into non-English languages, please do so via the web interface at [translate.shay.cat](https://translate.shay.cat/engage/discohook/), and not by editing these files directly. If you link your GitHub account to your Weblate account, you will be credited in your commits.

If you have any questions, coordinate with us on the [Discord server](https://discohook.app/discord) - we have a channel for translators.

```

### File: `packages/bot-rw/src/i18n/en-GB.json`
```json
{
  "customize": "Customise"
}

```

### File: `packages/bot-rw/src/i18n/en.json`
```json
{
  "commands": {
    "_options": {
      "webhook": {
        "name": "webhook",
        "description": "The target webhook"
      },
      "filter-channel": {
        "name": "filter-channel",
        "description": "The channel to filter autocomplete results with"
      }
    },
    "buttons": {
      "name": "buttons",
      "description": "Add, remove, and manage components (buttons/selects)",
      "options": {
        "add": {
          "name": "add",
          "description": "Add a component",
          "options": {
            "message": {
              "name": "message",
              "description": "Add a component to this message. A message link is also accepted here"
            },
            "channel": {
              "name": "channel",
              "description": "The channel that the message is in, for autocomplete results"
            }
          }
        },
        "edit": {
          "name": "edit",
          "description": "Edit a component",
          "options": {
            "message": {
              "name": "message",
              "description": "Edit a component on this message. A message link is also accepted here"
            },
            "channel": {
              "name": "channel",
              "description": "The channel that the message is in, for autocomplete results"
            }
          }
        },
        "delete": {
          "name": "delete",
          "description": "Delete a component",
          "options": {
            "message": {
              "name": "message",
              "description": "Delete a component on this message. A message link is also accepted here"
            },
            "channel": {
              "name": "channel",
              "description": "The channel that the message is in, for autocomplete results"
            }
          }
        },
        "migrate": {
          "name": "migrate",
          "description": "Migrate all legacy buttons",
          "options": {
            "message": {
              "name": "message",
              "description": "Migrate components on this message. A message link is also accepted here"
            },
            "channel": {
              "name": "channel",
              "description": "The channel that the message is in, for autocomplete results"
            }
          }
        }
      }
    },
    "deluxe": {
      "name": "deluxe",
      "description": "Synchronize your Deluxe subscription",
      "options": {
        "info": {
          "name": "info",
          "description": "Info about Discohook Deluxe, our premium subscription option"
        },
        "sync": {
          "name": "sync",
          "description": "Make sure the Discohook website is up to date with your Deluxe subscription"
        }
      }
    },
    "triggers": {
      "description": "Set up triggers to respond to events in your server",
      "options": {
        "add": {
          "name": "add",
          "description": "Add a new trigger",
          "options": {
            "name": {
              "name": "name",
              "description": "The name of the trigger"
            },
            "event": {
              "name": "event",
              "description": "The event that will set off the trigger",
              "choices": {
                "0": "Member Join",
                "1": "Member Remove"
              }
            }
          }
        },
        "view": {
          "name": "view",
          "description": "View & manage a trigger",
          "options": {
            "name": {
              "name": "name",
              "description": "The name of the trigger"
            }
          }
        }
      }
    },
    "webhook": {
      "name": "webhook",
      "description": "Manage webhooks",
      "options": {
        "create": {
          "name": "create",
          "description": "Create a webhook",
          "options": {
            "name": {
              "name": "name",
              "description": "The webhook's name"
            },
            "avatar": {
              "name": "avatar",
              "description": "The webhook's avatar"
            },
            "channel": {
              "name": "channel",
              "description": "The channel to create the webhook in"
            },
            "show-url": {
              "name": "show-url",
              "description": "Only enable this if you need the URL for an external application"
            }
          }
        },
        "delete": {
          "name": "delete",
          "description": "Delete a webhook",
          "options": {
            "webhook": {
              "name": "webhook",
              "description": "The webhook to delete"
            },
            "filter-channel": {
              "name": "filter-channel",
              "description": "The channel to filter autocomplete results with"
            }
          }
        },
        "info": {
          "name": "info",
          "description": "Get info on a webhook",
          "options": {
            "webhook": {
              "name": "webhook",
              "description": "The webhook to get info for"
            },
            "filter-channel": {
              "name": "filter-channel",
              "description": "The channel to filter autocomplete results with"
            },
            "show-url": {
              "name": "show-url",
              "description": "Whether to skip the \"Get URL\" step. This makes the message hidden"
            }
          }
        }
      }
    },
    "welcomer": {
      "name": "welcomer",
      "description": "Set up a simple welcomer (Also see /triggers)",
      "options": {
        "set": {
          "name": "set",
          "description": "Set up a new welcomer or overwrite an existing one",
          "options": {
            "event": {
              "name": "event",
              "description": "What event should cause this welcomer to trigger",
              "choices": {
                "0": "Member Join (hello)",
                "1": "Member Remove (goodbye)"
              }
            },
            "channel": {
              "name": "channel",
              "description": "The channel to send the message in if a webhook is not provided"
            },
            "webhook": {
              "name": "webhook",
              "description": "The webhook to use to send the message"
            },
            "share-link": {
              "name": "share-link",
              "description": "The share link to use for the message"
            },
            "delete-after": {
              "name": "delete-after",
              "description": "How long to wait in seconds before deleting the message (0 for never)"
            }
          }
        },
        "view": {
          "name": "view",
          "description": "View a summary of your current welcomer configuration",
          "options": {
            "event": {
              "name": "event",
              "description": "The event of the welcomer"
            }
          }
        },
        "delete": {
          "name": "delete",
          "description": "Delete a welcomer configuration",
          "options": {
            "event": {
              "name": "event",
              "description": "The event of the welcomer"
            }
          }
        }
      }
    },
    "profile": {
      "name": "profile",
      "description": "Configure the server profile for Discohook Utils",
      "options": {
        "set": {
          "name": "set",
          "description": "Override the bot's nickname, avatar, or banner with custom values",
          "options": {
            "name": {
              "name": "name",
              "description": "The bot's nickname"
            },
            "avatar": {
              "name": "avatar",
              "description": "The bot's avatar"
            },
            "banner": {
              "name": "banner",
              "description": "The bot's banner"
            }
          }
        },
        "clear": {
          "name": "clear",
          "description": "Reset one or all profile values to their defaults",
          "options": {
            "value": {
              "name": "value",
              "description": "Which value to reset. If not provided, all values are cleared"
            }
          }
        }
      }
    },
    "help": {
      "description": "Get help with various topics",
      "options": {
        "tag": {
          "name": "tag",
          "description": "The tag to get help for"
        },
        "mention": {
          "name": "mention",
          "description": "If you are helping someone else, mention them in the bot reply"
        }
      }
    },
    "reaction-role": {
      "name": "reaction-role",
      "description": "Add, remove, and manage reaction roles",
      "options": {
        "create": {
          "name": "create",
          "description": "Create a new reaction role",
          "options": {
            "message": {
              "name": "message",
              "description": "The message to create the reaction on. A message link is also accepted here"
            },
            "emoji": {
              "name": "emoji",
              "description": "The emoji that the reaction should show. For external emojis, react before the bot"
            },
            "role": {
              "name": "role",
              "description": "The role that should be assigned/removed when the reaction is clicked"
            },
            "channel": {
              "name": "channel",
              "description": "The channel that the message is in, for autocomplete results"
            }
          }
        },
        "delete": {
          "name": "delete",
          "description": "Delete a reaction role from a message",
          "options": {
            "message": {
              "name": "message",
              "description": "The message to delete the reaction role from. A message link is also accepted here"
            },
            "emoji": {
              "name": "emoji",
              "description": "The emoji that the reaction shows. Omit this parameter to view a deletion menu"
            },
            "channel": {
              "name": "channel",
              "description": "The channel that the message is in, for autocomplete results"
            }
          }
        },
        "list": {
          "name": "list",
          "description": "List all reaction roles on a message",
          "options": {
            "message": {
              "description": "The message to list reaction roles on. A message link is also accepted here"
            },
            "channel": {
              "description": "The channel that the message is in, for autocomplete results"
            }
          }
        }
      }
    },
    "restore": {
      "name": "restore",
      "description": "Restore a message to the Discohook editor",
      "options": {
        "message": {
          "name": "message",
          "description": "The message to restore. A message link is also accepted here"
        },
        "mode": {
          "name": "mode",
          "description": "How to restore the message. Currently this only allows including edit options",
          "choices": {
            "edit": "With edit options",
            "link": "To link embed editor"
          }
        }
      }
    },
    "format": {
      "name": "format",
      "description": "Get markdown formatting for users, roles, channels, and emojis",
      "options": {
        "mention": {
          "name": "mention",
          "description": "Outputs the mention format for a user or role",
          "options": {
            "target": {
              "name": "target",
              "description": "The user or role to mention"
            }
          }
        },
        "channel": {
          "name": "channel",
          "description": "Outputs the mention format for a channel",
          "options": {
            "target": {
              "name": "target",
              "description": "The channel to mention"
            }
          }
        },
        "emoji": {
          "name": "emoji",
          "description": "Outputs the usage format for a server emoji",
          "options": {
            "target": {
              "name": "target",
              "description": "The emoji to use"
            }
          }
        }
      }
    },
    "invite": {
      "name": "invite",
      "description": "Invite URL for this bot"
    },
    "id": {
      "name": "id",
      "description": "Get the numeric ID of a Discord resource",
      "options": {
        "mention": {
          "name": "mention",
          "description": "Outputs the ID for a user or role",
          "options": {
            "target": {
              "name": "target",
              "description": "The user or role"
            }
          }
        },
        "channel": {
          "name": "channel",
          "description": "Outputs the ID for a channel or thread",
          "options": {
            "target": {
              "name": "target",
              "description": "The channel or thread"
            }
          }
        },
        "emoji": {
          "name": "emoji",
          "description": "Outputs the ID for a server emoji",
          "options": {
            "target": {
              "name": "target",
              "description": "The emoji"
            }
          }
        }
      }
    },
    "_ctx": {
      "components": {
        "name": "Buttons & Components"
      },
      "edit": {
        "name": "Quick Edit"
      },
      "restore": {
        "name": "Restore"
      },
      "webhook": {
        "name": "Webhook Info"
      },
      "quickedit": {
        "name": "Quick Edit"
      },
      "debug": {
        "name": "Debug"
      }
    }
  },
  "noMigratableComponents": "This message has no registered, migratable components.",
  "noContentAvailable": "No content available",
  "noComponentFlow": "There was no flow registered for this component. Click the button to configure a new flow.",
  "noComponentFlowMigratePrompt": "You may need to run </buttons migrate:908884724087410729> if this message has buttons from before September 5, 2024.",
  "componentWillExpire": "Please finish editing & submit this component within 2 weeks or the draft will be deleted.",
  "noTrigger": "This server has no trigger with that name.",
  "unnamedTrigger": "Unnamed trigger",
  "triggerDuplicate": "This server already has a trigger for that event.",
  "triggerCreated": "Trigger **{{name}}** created successfully.",
  "addActions": "Add Actions",
  "noActions": "No actions",
  "manageActions": "Manage Actions",
  "idUnavailable": "ID unavailable.",
  "customize": "Customize",
  "gteNMessagesSent_one": "At least {{count}} message sent",
  "gteNMessagesSent_other": "At least {{count}} messages sent",
  "webhookDelete": {
    "confirm": "Are you sure you want to delete this webhook? This will make it impossible to edit any messages it has sent.",
    "forbidden": "You don't have permissions to manage webhooks.",
    "wrongServer": "Webhook does not exist or it is not in this server.",
    "success": "Deleted the webhook successfully.",
    "cancel": "The webhook is safe and sound."
  }
}

```

### File: `packages/bot-rw/src/i18n/fr.json`
```json
{
  "commands": {
    "invite": {
      "name": "ajouter"
    },
    "webhook": {
      "options": {
        "create": {
          "name": "créer",
          "description": "Créer un webhook",
          "options": {
            "name": {
              "name": "nom",
              "description": "Le nom du webhook"
            },
            "channel": {
              "name": "salon",
              "description": "Le canal dans lequel créer le webhook"
            },
            "avatar": {
              "description": "L'avatar du webhook"
            },
            "show-url": {
              "description": "Activez ce paramètre uniquement si vous avez besoin de l'URL pour une application externe"
            }
          }
        },
        "delete": {
          "name": "supprimer",
          "description": "Supprimer un webhook",
          "options": {
            "webhook": {
              "name": "webhook",
              "description": "Le webhook à supprimer"
            },
            "filter-channel": {
              "name": "filtrer",
              "description": "Filtrer les résultats par salon"
            }
          }
        },
        "info": {
          "name": "info",
          "options": {
            "webhook": {
              "name": "webhook",
              "description": "Sélectionner un webhook"
            },
            "filter-channel": {
              "description": "Filtrer les résultats par salon",
              "name": "filtre"
            },
            "show-url": {
              "name": "afficher-url"
            }
          },
          "description": "Afficher des infos sur un webhook"
        }
      },
      "description": "Gérer les webhooks"
    },
    "buttons": {
      "description": "Ajouter, supprimer ou gérer les composants",
      "options": {
        "add": {
          "options": {
            "channel": {
              "description": "Le salon dans lequel le message est posté, pour l'autocomplétion"
            },
            "message": {
              "description": "Ajouter un composant à ce message (un lien de message marche aussi)"
            }
          },
          "description": "Ajouter un composant"
        },
        "edit": {
          "description": "Modifier un composant",
          "options": {
            "message": {
              "description": "Modifie un des composants de ce message (un lien de message est aussi accepté)"
            },
            "channel": {
              "description": "Le salon dans lequel ce message a été posté",
              "name": "salon"
            }
          }
        },
        "delete": {
          "description": "Supprime un composant",
          "options": {
            "message": {
              "description": "Supprime un des composants de ce message (un lien de message est également accepté)"
            }
          },
          "name": "supprimé"
        }
      }
    },
    "deluxe": {
      "options": {
        "info": {
          "name": "information",
          "description": "Affiche des infos sur Discohook Deluxe, notre offre premium"
        },
        "sync": {
          "name": "synchroniser",
          "description": "Vérifie que le site Discohook a pris en compte votre abonnement Deluxe"
        }
      }
    },
    "_options": {
      "webhook": {
        "description": "Sélectionnez un webhook"
      },
      "filter-channel": {
        "description": "Filtre les résultats de l'autocomplétion en fonction de ce salon"
      }
    },
    "help": {
      "description": "Obtenir de l'aide",
      "options": {
        "tag": {
          "description": "Choisir un sujet",
          "name": "tag"
        },
        "mention": {
          "name": "mention",
          "description": "Si vous aidez quelqu'un, la personne sera mentionnée dans le message"
        }
      }
    },
    "reaction-role": {
      "options": {
        "create": {
          "options": {
            "role": {
              "description": "Le rôle qui doit être assigné ou retiré quand la réaction est cliquée"
            },
            "message": {
              "description": "Sur quel message ajouter la réaction ? Un lien de message marche"
            },
            "emoji": {
              "description": "Choisissez un emoji pour la réaction, si il est custom, réagissez avant le bot"
            }
          },
          "description": "Créer un nouveau rôle-réaction"
        },
        "delete": {
          "description": "Supprime un rôle-réaction d'un message",
          "options": {
            "message": {
              "description": "De quel message retirer le rôle-réaction ? Un lien de message marche"
            }
          }
        }
      }
    },
    "triggers": {
      "options": {
        "add": {
          "description": "Ajouter un nouveau déclencheur",
          "options": {
            "name": {
              "description": "Nom du déclencheur"
            },
            "event": {
              "choices": {
                "1": "Un membre a quitté",
                "0": "Un membre a rejoint"
              },
              "description": "L'événement déclencheur"
            }
          }
        },
        "view": {
          "description": "Voir et gérer un déclencheur",
          "options": {
            "name": {
              "description": "Nom du déclencheur"
            }
          }
        }
      },
      "description": "Configurez des déclencheurs pour réagir à des événements dans votre serveur"
    }
  }
}

```

### File: `packages/bot-rw/src/i18n/it.json`
```json
{
  "commands": {
    "buttons": {
      "description": "Aggiungi, rimuovi, e gestisci i componenti (bottoni/tendine)",
      "options": {
        "migrate": {
          "description": "Migra tutti i bottoni legacy",
          "options": {
            "message": {
              "name": "messaggio",
              "description": "Migra tutti i componenti di questo messaggio. Anche un link di un messaggio è accettabile qui"
            },
            "channel": {
              "name": "canale",
              "description": "Il canale nel quale si trova il messaggio, per i risultati di autocompletamento"
            }
          },
          "name": "migra"
        },
        "add": {
          "name": "aggiungi",
          "description": "Aggiungi un componente",
          "options": {
            "channel": {
              "name": "canale",
              "description": "Il canale nel quale si trova il messaggio, per i risultati di autocompletamento"
            },
            "message": {
              "description": "Aggiungi un componente a questo messaggio. Anche un link di un messaggio è accettabile qui",
              "name": "messaggio"
            }
          }
        },
        "edit": {
          "name": "modifica",
          "options": {
            "message": {
              "name": "messaggio",
              "description": "Modifica un componente di questo messaggio. Anche un link di un messaggio è accettabile qui"
            },
            "channel": {
              "name": "canale",
              "description": "Il canale nel quale si trova il messaggio, per i risultati di autocompletamento"
            }
          },
          "description": "Modifica un componente"
        },
        "delete": {
          "name": "elimina",
          "options": {
            "message": {
              "name": "messaggio",
              "description": "Elimina un componente in questo messaggio. Anche un link di un messaggio è accettabile qui"
            },
            "channel": {
              "name": "canale",
              "description": "Il canale nel quale si trova il messaggio, per i risultati di autocompletamento"
            }
          },
          "description": "Elimina un componente"
        }
      },
      "name": "bottoni"
    },
    "_options": {
      "webhook": {
        "name": "webhook",
        "description": "Il webhook bersaglio"
      },
      "filter-channel": {
        "name": "filtra-canale",
        "description": "Il canale in cui filtrare i risultati dell'autocompletamento"
      }
    },
    "deluxe": {
      "name": "deluxe",
      "description": "Sincronizza la tua iscrizione a Deluxe",
      "options": {
        "info": {
          "name": "informazioni",
          "description": "Informazioni su Discohook Deluxe, la nostra opzione di iscrizione premium"
        },
        "sync": {
          "name": "sincronizzazione",
          "description": "Assicurati che il sito di Discohook sia aggiornato con la tua iscrizione Deluxe"
        }
      }
    },
    "triggers": {
      "description": "Imposta dei trigger per rispondere ad avvenimenti nel tuo server",
      "options": {
        "add": {
          "name": "aggiungi",
          "description": "Aggiungi un nuovo trigger",
          "options": {
            "name": {
              "name": "nome",
              "description": "Il nome del trigger"
            },
            "event": {
              "name": "evento",
              "description": "L'avvenimento che farà scattare il trigger",
              "choices": {
                "0": "Unione di un Utente",
                "1": "Rimozione di un Utente"
              }
            }
          }
        },
        "view": {
          "description": "Visualizza e gestisci un trigger",
          "options": {
            "name": {
              "name": "nome",
              "description": "Il nome del trigger"
            }
          },
          "name": "visualizza"
        }
      }
    },
    "webhook": {
      "name": "webhook",
      "description": "Gestisci i webhook",
      "options": {
        "create": {
          "name": "crea",
          "description": "Crea un webhook",
          "options": {
            "name": {
              "name": "nome",
              "description": "Il nome del webhook"
            },
            "avatar": {
              "description": "L'immagine di profilo del webhook"
            },
            "channel": {
              "name": "canale",
              "description": "Il canale in cui verrà creato il webhook"
            },
            "show-url": {
              "name": "mostra-url",
              "description": "Attiva questa opzione solo se ti serve l'URL del webhook per un'applicazione esterna"
            }
          }
        },
        "delete": {
          "name": "cancella",
          "description": "Cancella un webhook",
          "options": {
            "webhook": {
              "name": "webhook",
              "description": "Il webhook da eliminare"
            },
            "filter-channel": {
              "name": "filtra-canale",
              "description": "Il canale in cui filtrare i risultati di autocompletamento"
            }
          }
        },
        "info": {
          "name": "informazioni",
          "description": "Ottieni informazioni su un webhook",
          "options": {
            "webhook": {
              "name": "webhook",
              "description": "Il webhook del quale vuoi ottenere informazioni"
            },
            "filter-channel": {
              "name": "filtra-canale",
              "description": "Il canale in cui filtrare i risultati di autocompletamento"
            },
            "show-url": {
              "name": "mostra-url"
            }
          }
        }
      }
    }
  }
}

```

### File: `packages/bot-rw/src/i18n/nl.json`
```json
{
  "commands": {
    "_options": {
      "webhook": {
        "description": "De webhook"
      },
      "filter-channel": {
        "name": "kanaal",
        "description": "Het kanaal waar de webhook is, voor het automatisch aanvullen van resultaten"
      }
    },
    "buttons": {
      "name": "knoppen",
      "description": "Onderdelen toevoegen, verwijderen, en beheren",
      "options": {
        "add": {
          "name": "toevoegen",
          "description": "Voeg een onderdeel toe",
          "options": {
            "message": {
              "description": "Het bericht om de knop toe te voegen, een berichtenlink wordt hier geaccepteerd"
            },
            "channel": {
              "name": "kanaal",
              "description": "Het kanaal waar het bericht is, voor het automatisch aanvullen van resultaten"
            }
          }
        },
        "edit": {
          "description": "Bewerk onderdeel",
          "options": {
            "message": {
              "description": "Bewerk een onderdeel van dit bericht, een berichtenlink is hier ook toegestaan"
            },
            "channel": {
              "description": "The kanaal waar het bericht in staat, voor autosuggestie resultaat"
            }
          }
        },
        "delete": {
          "options": {
            "channel": {
              "description": "Het kanaal waar het bericht in staat, voor autosuggestie resultaten"
            },
            "message": {
              "description": "Verwijder een onderdeel van dit bericht. Een berichtenlink is hier ook toegestaan"
            }
          },
          "description": "Verwijder een onderdeel"
        }
      }
    },
    "format": {
      "name": "opmaak",
      "options": {
        "mention": {
          "name": "melding",
          "description": "Geeft de opmaak voor een melding van een serverlid of rol",
          "options": {
            "target": {
              "name": "doel",
              "description": "Het serverlid of rol om te melden"
            }
          }
        },
        "channel": {
          "name": "kanaal",
          "description": "Geeft de opmaak voor het noemen van een kanaal",
          "options": {
            "target": {
              "name": "doel",
              "description": "Het kanaal om te noemen"
            }
          }
        },
        "emoji": {
          "description": "Geeft de opmaak om een server emoji te gebruiken",
          "options": {
            "target": {
              "name": "doel",
              "description": "De emoji"
            }
          }
        }
      }
    },
    "invite": {
      "name": "toevoegen",
      "description": "Link om mij toe te voegen aan een andere server"
    },
    "webhook": {
      "description": "Webhooks beheren",
      "options": {
        "create": {
          "name": "creëer",
          "description": "Creëer een webhook",
          "options": {
            "name": {
              "name": "naam",
              "description": "De webhook's naam"
            },
            "avatar": {
              "description": "De webhook's avatar"
            },
            "channel": {
              "name": "kanaal",
              "description": "Het kanaal om de webhook in te maken"
            },
            "show-url": {
              "name": "toon-url",
              "description": "Gebruik dit alleen als je de URL nodig hebt voor een externe applicatie"
            }
          }
        },
        "delete": {
          "name": "verwijder",
          "description": "Verwijder een webhook"
        },
        "info": {
          "description": "Verkrijg informatie over een webhook",
          "options": {
            "show-url": {
              "name": "toon-url",
              "description": "Of je de \"Verkrijg URL\" stap over wilt slaan. Dit maakt het bericht verborgen"
            }
          }
        }
      }
    },
    "help": {
      "description": "Krijg hulp met verschillende onderwerpen",
      "options": {
        "tag": {
          "name": "onderwerp",
          "description": "Het onderwerp waar je hulp bij kunt krijgen"
        }
      }
    },
    "reaction-role": {
      "name": "reactie-rol",
      "options": {
        "create": {
          "name": "creëer",
          "description": "Creëer een nieuwe reactie rol",
          "options": {
            "message": {
              "name": "bericht",
              "description": "Het bericht om een reactie rol op te maken, een berichtenlink wordt hier geaccepteerd"
            },
            "emoji": {
              "description": "De emoji die de reactie moet laten zien. Voor externe emoji: reageer voor get gebruik van de bot"
            },
            "role": {
              "name": "rol",
              "description": "De rol die moet worden toegewezen of verwijderd wanneer de reactie gebruikt wordt"
            },
            "channel": {
              "name": "kanaal",
              "description": "Het kanaal waar het bericht is, voor het automatisch aanvullen van resultaten"
            }
          }
        },
        "delete": {
          "description": "Verwijder een reactie rol",
          "options": {
            "message": {
              "name": "bericht",
              "description": "Het bericht om een reactie rol van te verwijderen, een berichtenlink wordt hier geaccepteerd"
            },
            "emoji": {
              "description": "De emoji dat de reactie rol laat zien. Laat dit weg voor een verwijdermenu"
            },
            "channel": {
              "name": "kanaal",
              "description": "Het kanaal waar het bericht is, voor het automatisch aanvullen van resultaten"
            }
          }
        }
      }
    },
    "_ctx": {
      "components": {
        "name": "Knoppen & Componenten"
      },
      "edit": {
        "name": "Snelle Bewerking"
      },
      "restore": {
        "name": "Herstel"
      },
      "webhook": {
        "name": "Webhook Info"
      },
      "debug": {
        "name": "Debug"
      }
    },
    "triggers": {
      "description": "Stel triggers in om te reageren op gebeurtenissen in je server",
      "options": {
        "add": {
          "description": "Voeg een nieuwe trigger toe",
          "options": {
            "name": {
              "description": "De naam van de trigger"
            },
            "event": {
              "description": "De gebeurtenis die de trigger zou activeren",
              "choices": {
                "0": "Iemand wordt lid van de server",
                "1": "Iemand verlaat de server"
              }
            }
          }
        },
        "view": {
          "description": "Bekijk en beheer een trigger",
          "options": {
            "name": {
              "description": "De naam van de trigger"
            }
          }
        }
      }
    },
    "welcomer": {
      "description": "Welkomstberichten zijn verhuisd naar /triggers!"
    }
  }
}

```

### File: `packages/bot-rw/src/i18n/ru.json`
```json
{
  "commands": {
    "_options": {
      "webhook": {
        "name": "вебхук"
      }
    }
  }
}

```

### File: `packages/bot-rw/src/i18n/uk.json`
```json
{}

```

### File: `packages/bot-rw/src/i18n/zh-CN.json`
```json
{
  "commands": {
    "buttons": {
      "options": {
        "add": {
          "description": "添加组件"
        },
        "delete": {
          "description": "删除组件"
        }
      },
      "description": "添加、删除和管理组件"
    },
    "_ctx": {
      "edit": {
        "name": "快速编辑"
      },
      "restore": {
        "name": "恢复消息"
      },
      "webhook": {
        "name": "Webhook 信息"
      },
      "components": {
        "name": "按钮 & 组件"
      }
    },
    "webhook": {
      "description": "管理 Webhook",
      "options": {
        "create": {
          "description": "创建一个 Webhook",
          "options": {
            "name": {
              "description": "Webhook 名称"
            },
            "avatar": {
              "description": "Webhook 的头像"
            }
          },
          "name": "创建"
        },
        "info": {
          "options": {
            "webhook": {
              "name": "webhook"
            }
          }
        },
        "delete": {
          "options": {
            "webhook": {
              "name": "webhook"
            }
          },
          "name": "删除",
          "description": "删除 Webhook"
        }
      }
    },
    "triggers": {
      "options": {
        "add": {
          "options": {
            "event": {
              "choices": {
                "0": "成员加入",
                "1": "成员移除"
              }
            }
          }
        }
      }
    },
    "deluxe": {
      "options": {
        "sync": {
          "name": "同步"
        }
      }
    }
  }
}

```

