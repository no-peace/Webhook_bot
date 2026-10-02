# Repository Context Group: pkg_bot_i18n
# Source Repository: discohook/discohook

### File: `packages/bot/src/i18n/README.md`
```md
# Contributing translations to Discohook

Hello. If you would like to help translate Discohook into non-English languages, please do so via the web interface at [translate.shay.cat](https://translate.shay.cat/engage/discohook/), and not by editing these files directly. If you link your GitHub account to your Weblate account, you will be credited in your commits.

If you have any questions, coordinate with us on the [Discord server](https://discohook.app/discord) - we have a channel for translators.

```

### File: `packages/bot/src/i18n/en-GB.json`
```json
{
  "customize": "Customise"
}

```

### File: `packages/bot/src/i18n/en.json`
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
            },
            "bio": {
              "name": "bio",
              "description": "The bot's bio. On desktop, use Shift + Enter for multiple lines"
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

### File: `packages/bot/src/i18n/fr.json`
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
            "description": "Ajouter, supprimer et gérez les composants (Boutons et selections)",
            "options": {
                "add": {
                    "options": {
                        "channel": {
                            "description": "Le salon dans lequel le message est posté, pour l'autocomplétion",
                            "name": "salon"
                        },
                        "message": {
                            "description": "Ajouter un composant à ce message (un lien de message marche aussi)",
                            "name": "message"
                        }
                    },
                    "description": "Ajouter un composant"
                },
                "edit": {
                    "description": "Modifier un composant",
                    "options": {
                        "message": {
                            "description": "Modifie un des composants de ce message (un lien de message est aussi accepté)",
                            "name": "message"
                        },
                        "channel": {
                            "description": "Le salon dans lequel ce message a été posté",
                            "name": "salon"
                        }
                    },
                    "name": "modifier"
                },
                "delete": {
                    "description": "Supprime un composant",
                    "options": {
                        "message": {
                            "description": "Supprime un des composants de ce message (un lien de message est également accepté)"
                        },
                        "channel": {
                            "name": "salon"
                        }
                    },
                    "name": "supprimé"
                },
                "migrate": {
                    "description": "Migrer tous les boutons hérités",
                    "options": {
                        "message": {
                            "description": "Migrer les composants de ce message. Un lien de message est également accepté ici",
                            "name": "message"
                        },
                        "channel": {
                            "name": "salon"
                        }
                    },
                    "name": "migration"
                }
            },
            "name": "boutons"
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
            },
            "description": "Synchronizer ton abonnement Deluxe"
        },
        "_options": {
            "webhook": {
                "description": "Sélectionnez un webhook",
                "name": "webhook"
            },
            "filter-channel": {
                "description": "Filtre les résultats de l'autocomplétion en fonction de ce salon",
                "name": "filtre-chaine"
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
    },
    "webhookDelete": {
        "confirm": "Êtes-vous sûr de vouloir supprimer ce webhook ? Cela rendra impossible la modification des messages qu'il a envoyés.",
        "forbidden": "Vous n'avez pas les autorisations pour gérer les webhooks.",
        "wrongServer": "Le webhook n'existe pas ou n'est pas sur ce serveur.",
        "success": "Le webhook a été supprimé avec succès.",
        "cancel": "Le webhook est sain et sauf."
    }
}

```

### File: `packages/bot/src/i18n/he.json`
```json
{}

```

### File: `packages/bot/src/i18n/it.json`
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

### File: `packages/bot/src/i18n/nl.json`
```json
{
    "commands": {
        "_options": {
            "webhook": {
                "description": "De webhook",
                "name": "webhook"
            },
            "filter-channel": {
                "name": "kanaal",
                "description": "Het kanaal waar de webhook is, voor het automatisch aanvullen van resultaten"
            }
        },
        "buttons": {
            "name": "knoppen",
            "description": "Onderdelen toevoegen, verwijderen, en beheren (buttons/selects)",
            "options": {
                "add": {
                    "name": "toevoegen",
                    "description": "Voeg een onderdeel toe",
                    "options": {
                        "message": {
                            "description": "Voeg een component toe, een berichtenlink wordt hier ook geaccepteerd",
                            "name": "bericht"
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
                            "description": "Bewerk een onderdeel van dit bericht, een berichtenlink is hier ook toegestaan",
                            "name": "bericht"
                        },
                        "channel": {
                            "description": "The kanaal waar het bericht in staat, voor autosuggestie resultaat",
                            "name": "kanaal"
                        }
                    },
                    "name": "bewerk"
                },
                "delete": {
                    "options": {
                        "channel": {
                            "description": "Het kanaal waar het bericht in staat, voor autosuggestie resultaten",
                            "name": "kanaal"
                        },
                        "message": {
                            "description": "Verwijder een onderdeel van dit bericht. Een berichtenlink is hier ook toegestaan",
                            "name": "bericht"
                        }
                    },
                    "description": "Verwijder een onderdeel",
                    "name": "verwijder"
                },
                "migrate": {
                    "description": "Migreer alle legacy knoppen",
                    "name": "migreer",
                    "options": {
                        "message": {
                            "name": "bericht",
                            "description": "Migreer componenten op dit bericht. Een berichtlink wordt hier ook geaccepteerd"
                        },
                        "channel": {
                            "description": "Het kanaal waarin het bericht zich bevindt, voor resultaten van automatisch aanvullen",
                            "name": "kanaal"
                        }
                    }
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
            },
            "name": "webhook"
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
                            "description": "De naam van de trigger",
                            "name": "naam"
                        },
                        "event": {
                            "description": "De gebeurtenis die de trigger zou activeren",
                            "choices": {
                                "0": "Iemand wordt lid van de server",
                                "1": "Iemand verlaat de server"
                            }
                        }
                    },
                    "name": "voeg-toe"
                },
                "view": {
                    "description": "Bekijk en beheer een trigger",
                    "options": {
                        "name": {
                            "description": "De naam van de trigger",
                            "name": "naam"
                        }
                    }
                }
            }
        },
        "welcomer": {
            "description": "Welkomstberichten zijn verhuisd naar /triggers!"
        },
        "deluxe": {
            "name": "deluxe",
            "options": {
                "info": {
                    "name": "informatie",
                    "description": "Informatie over Discohook Deluxe, onze premium abonnementsoptie"
                },
                "sync": {
                    "name": "synchroniseren",
                    "description": "Zorg ervoor dat de Discohook-website up-to-date is met je Deluxe-abonnement"
                }
            },
            "description": "Synchroniseer je Deluxe-abonnement"
        }
    }
}

```

### File: `packages/bot/src/i18n/pl.json`
```json
{
    "commands": {
        "_options": {
            "webhook": {
                "name": "webhook"
            }
        }
    }
}

```

### File: `packages/bot/src/i18n/ro.json`
```json
{}

```

### File: `packages/bot/src/i18n/ru.json`
```json
{
    "commands": {
        "_options": {
            "webhook": {
                "name": "вебхук",
                "description": "Цель вебхука"
            },
            "filter-channel": {
                "description": "Канал, по которому фильтруются результаты автозаполнения",
                "name": "фильтр-канала"
            }
        },
        "buttons": {
            "options": {
                "add": {
                    "options": {
                        "message": {
                            "description": "Добавить компонент к этому сообщению. Можно также указать ссылку на сообщение",
                            "name": "сообщение"
                        },
                        "channel": {
                            "description": "Канал, в котором находится сообщение (для автозаполнения)",
                            "name": "канал"
                        }
                    },
                    "name": "добавить",
                    "description": "Добавить компонент"
                },
                "delete": {
                    "options": {
                        "message": {
                            "description": "Редактировать компонент в этом сообщении. Можно также указать ссылку на сообщение",
                            "name": "сообщение"
                        },
                        "channel": {
                            "name": "канал",
                            "description": "Канал, в котором находится сообщение (для автозаполнения)"
                        }
                    },
                    "description": "Удалить компонент",
                    "name": "удалить"
                },
                "migrate": {
                    "options": {
                        "channel": {
                            "description": "Канал, в котором находится сообщение (для автозаполнения)",
                            "name": "канал"
                        },
                        "message": {
                            "name": "сообщение",
                            "description": "Перенести компоненты в этом сообщении. Можно также указать ссылку на сообщение"
                        }
                    },
                    "name": "мигрировать",
                    "description": "Перенести все устаревшие кнопки"
                },
                "edit": {
                    "options": {
                        "message": {
                            "description": "Редактировать компонент в этом сообщении. Можно также указать ссылку на сообщение",
                            "name": "сообщение"
                        },
                        "channel": {
                            "description": "Канал, в котором находится сообщение (для автозаполнения)",
                            "name": "канал"
                        }
                    },
                    "name": "редактировать",
                    "description": "Редактировать компонент"
                }
            },
            "description": "Добавление, удаление компонентов и управление ими (кнопки/выбор)",
            "name": "кнопки"
        },
        "triggers": {
            "options": {
                "view": {
                    "description": "Просмотр и управление триггером",
                    "options": {
                        "name": {
                            "name": "имя",
                            "description": "Имя триггера"
                        }
                    },
                    "name": "просмотр"
                },
                "add": {
                    "options": {
                        "name": {
                            "name": "имя",
                            "description": "Название триггера"
                        },
                        "event": {
                            "description": "Событие, которое запустит триггер",
                            "choices": {
                                "0": "Присоединение участника",
                                "1": "Удаление участника"
                            },
                            "name": "событие"
                        }
                    },
                    "name": "добавить",
                    "description": "Добавить новый триггер"
                }
            },
            "description": "Настройте триггеры для реагирования на события на вашем сервере"
        },
        "webhook": {
            "options": {
                "create": {
                    "options": {
                        "name": {
                            "description": "Имя вебхука",
                            "name": "имя"
                        },
                        "avatar": {
                            "name": "аватар",
                            "description": "Аватар вебхука"
                        },
                        "channel": {
                            "name": "канал",
                            "description": "Канал, в котором будет создан вебхук"
                        },
                        "show-url": {
                            "name": "показать-ссылку",
                            "description": "Включите эту опцию только в том случае, если вам нужен URL для внешнего приложения."
                        }
                    },
                    "description": "Создать вебхук",
                    "name": "создать"
                },
                "delete": {
                    "name": "удалить",
                    "description": "Удалить вебхук",
                    "options": {
                        "webhook": {
                            "name": "вебхук",
                            "description": "Вебхук, который нужно удалить"
                        },
                        "filter-channel": {
                            "name": "фильтр-канала",
                            "description": "Канал для фильтрации результатов (автозаполнения)"
                        }
                    }
                },
                "info": {
                    "options": {
                        "show-url": {
                            "name": "показать-ссылку",
                            "description": "Хотите ли вы пропустить этап \"Получить URL\"? Это приведет к скрытию сообщения"
                        },
                        "webhook": {
                            "name": "вебхук",
                            "description": "Вебхук, информацию о котором нужно получить"
                        },
                        "filter-channel": {
                            "name": "фильтр-канала",
                            "description": "Канал для фильтрации результатов автозаполнения с помощью"
                        }
                    },
                    "name": "информация",
                    "description": "Получить информацию о вебхуке"
                }
            },
            "name": "вебхук",
            "description": "Управление вебхуками"
        },
        "deluxe": {
            "options": {
                "sync": {
                    "description": "Убедитесь, что сайт Discohook обновлён в соответствии с вашей подпиской Deluxe",
                    "name": "синхронизация"
                },
                "info": {
                    "name": "информация",
                    "description": "Информация о Discohook Deluxe — нашей премиум-подписке"
                }
            },
            "name": "делюкс",
            "description": "Синхронизируйте вашу подписку Deluxe"
        },
        "welcomer": {
            "options": {
                "set": {
                    "options": {
                        "channel": {
                            "description": "Канал для отправки сообщение если webhook не указан",
                            "name": "канал"
                        },
                        "event": {
                            "name": "событие",
                            "description": "Какое событие должно запускать это приветствие",
                            "choices": {
                                "0": "Присоединение участника (приветствие)",
                                "1": "Удаление участника (прощание)"
                            }
                        },
                        "share-link": {
                            "name": "поделиться-ссылкой",
                            "description": "Ссылка для публикации в сообщении"
                        },
                        "delete-after": {
                            "name": "удалить-после",
                            "description": "Время в секундах перед тем как удалить сообщение (0 если никогда)"
                        },
                        "webhook": {
                            "name": "webhook",
                            "description": "Вебхук для отправки сообщения"
                        }
                    },
                    "name": "установить",
                    "description": "Настройте новое приветствие или перезапишите существующее"
                },
                "view": {
                    "name": "просмотр",
                    "options": {
                        "event": {
                            "name": "событие",
                            "description": "Событие приветствия"
                        }
                    },
                    "description": "Просмотреть сводку текущей конфигурации приветствия"
                },
                "delete": {
                    "name": "удалить",
                    "options": {
                        "event": {
                            "name": "событие",
                            "description": "Событие приветствия"
                        }
                    },
                    "description": "Удалить конфигурацию приветствия"
                }
            },
            "name": "приветствующий",
            "description": "Установите простого приветствия (Смотрите также /triggers)"
        },
        "profile": {
            "description": "Настройте профиль сервера для Discohook Utils",
            "options": {
                "set": {
                    "options": {
                        "banner": {
                            "description": "Баннер бота",
                            "name": "баннер"
                        },
                        "name": {
                            "name": "имя",
                            "description": "Никнейм бота"
                        },
                        "avatar": {
                            "name": "аватар",
                            "description": "Аватар бота"
                        }
                    },
                    "name": "установить",
                    "description": "Замените ник, аватар или баннер бота пользовательскими значениями"
                },
                "clear": {
                    "options": {
                        "value": {
                            "name": "значение",
                            "description": "Какое значение следует сбросить. Если это не указано, все значения будут удалены"
                        }
                    },
                    "name": "очистить",
                    "description": "Сброс одного или всех значений профиля к значениям по умолчанию"
                }
            },
            "name": "профиль"
        },
        "reaction-role": {
            "options": {
                "create": {
                    "description": "Создать новую роль за реакцию",
                    "name": "добавить",
                    "options": {
                        "message": {
                            "name": "сообщение",
                            "description": "Сообщение, на которое нужно поставить реакцию. Также можно вставить ссылку на сообщение."
                        },
                        "emoji": {
                            "name": "эмодзи",
                            "description": "Эмодзи, которое будет отображаться в реакции. Для внешних эмодзи поставьте реакцию до бота."
                        },
                        "role": {
                            "name": "роль",
                            "description": "Роль, которая будет добавлена/убрана, когда реакция нажата"
                        },
                        "channel": {
                            "name": "канал",
                            "description": "Канал, в котором находится сообщение, для результатов автозаполнения"
                        }
                    }
                },
                "delete": {
                    "name": "удалить",
                    "description": "Удалить роль за реакцию у сообщению",
                    "options": {
                        "message": {
                            "name": "сообщение",
                            "description": "Сообщение, из которого нужно удалить роль по реакции. Также можно вставить ссылку на сообщение."
                        },
                        "emoji": {
                            "name": "эмодзи",
                            "description": "Эмодзи, которое отображается в реакции. Не указывайте этот параметр, чтобы открыть меню удаления."
                        },
                        "channel": {
                            "name": "канал",
                            "description": "Канал, в котором находится сообщение, для результатов автозаполнения"
                        }
                    }
                },
                "list": {
                    "name": "список",
                    "description": "Список всех ролей за реакцию на сообщении",
                    "options": {
                        "channel": {
                            "description": "Канал, в котором находится сообщение, для результатов автозаполнения"
                        }
                    }
                }
            },
            "name": "роль-реакции",
            "description": "Добавить, удалить и управлять ролями за реакции"
        },
        "help": {
            "options": {
                "tag": {
                    "name": "тег",
                    "description": "Тег, по которому можно получить справку"
                },
                "mention": {
                    "name": "упоминание",
                    "description": "Если вы помогаете кому-то другому, упомяните его в ответе бота"
                }
            },
            "description": "Получить помощь по различным темам"
        },
        "restore": {
            "name": "восстановить",
            "description": "Восстановить сообщение в редакторе Discohook",
            "options": {
                "message": {
                    "name": "сообщение",
                    "description": "Сообщение, которое нужно восстановить. Также можно вставить ссылку на сообщение."
                },
                "mode": {
                    "name": "режим"
                }
            }
        }
    }
}

```

### File: `packages/bot/src/i18n/tr.json`
```json
{
    "commands": {
        "webhook": {
            "options": {
                "create": {
                    "options": {
                        "name": {
                            "name": "isim",
                            "description": "Webhook'un ismi"
                        },
                        "avatar": {
                            "name": "avatar",
                            "description": "Webhook'un avatarı"
                        },
                        "show-url": {
                            "description": "Bunu sadece bir üçüncü taraf uygulama için URL'ye ihtiyacın varsa aç",
                            "name": "url-göster"
                        },
                        "channel": {
                            "name": "kanal",
                            "description": "Webhook'un oluşturulacağı kanal"
                        }
                    },
                    "name": "oluştur",
                    "description": "Webhook oluştur"
                },
                "info": {
                    "options": {
                        "filter-channel": {
                            "description": "Oto-tamamlanan sonuçların filtreleneceği kanal",
                            "name": "filtre-kanal"
                        },
                        "webhook": {
                            "name": "webhook",
                            "description": "Bilgisini istediğin webhook"
                        },
                        "show-url": {
                            "name": "url-göster",
                            "description": "\"URL al\" adımının atlanması için. Mesajı gizler"
                        }
                    },
                    "name": "info",
                    "description": "Bir webhook hakkında bilgi al"
                },
                "delete": {
                    "name": "sil",
                    "description": "Bir webhook sil",
                    "options": {
                        "webhook": {
                            "name": "webhook",
                            "description": "Silinecek webhook"
                        },
                        "filter-channel": {
                            "name": "filtre-kanal",
                            "description": "Oto-tamamlanan sonuçların filtreleneceği kanal"
                        }
                    }
                }
            },
            "name": "webhook",
            "description": "Webhookları yönet"
        },
        "welcomer": {
            "options": {
                "delete": {
                    "options": {
                        "event": {
                            "name": "olay",
                            "description": "Karşılayıcının olayı"
                        }
                    },
                    "name": "sil",
                    "description": "Bir karşılama konfigürasyonu sil"
                },
                "set": {
                    "options": {
                        "event": {
                            "description": "Bu karşılayıcıyı hangi olayların tetikleyeceği",
                            "name": "olay",
                            "choices": {
                                "0": "Üye Katıldı (ağırlama)",
                                "1": "Üye Ayrıldı (geçirme)"
                            }
                        },
                        "share-link": {
                            "description": "Mesaj için kullanılacak paylaşım linki",
                            "name": "paylaşım-link"
                        },
                        "channel": {
                            "name": "kanal",
                            "description": "Eğer bir webhook belirtilmediyse, mesajın gönderileceği kanal"
                        },
                        "webhook": {
                            "name": "webhook",
                            "description": "Mesajı göndermek için kullanılacak webhook"
                        },
                        "delete-after": {
                            "name": "sonra-sil",
                            "description": "Mesajı silmeden önce kaç saniye bekleyeceği (0 = asla silme)"
                        }
                    },
                    "name": "set",
                    "description": "Yeni bir karşılama sistemi setuplayın veya var olanın üzerine yazın"
                },
                "view": {
                    "name": "görüntüle",
                    "description": "Karşılayıcı konfigürasyonunun özetini gör",
                    "options": {
                        "event": {
                            "name": "olay",
                            "description": "Karşılayıcının olayı"
                        }
                    }
                }
            },
            "name": "karşılayıcı",
            "description": "Basit bi karşılama sistemi hazırlayın (Bir de /triggers göz atın)"
        },
        "profile": {
            "name": "profil",
            "description": "Discohook Utils için sunucu profilini ayarla",
            "options": {
                "set": {
                    "name": "set",
                    "description": "Bot'un adını, avatarını, veya bannerını özel değerlerle değiştir",
                    "options": {
                        "name": {
                            "name": "isim",
                            "description": "Botun ismi"
                        },
                        "avatar": {
                            "name": "avatar",
                            "description": "Botun avatarı"
                        },
                        "banner": {
                            "name": "banner",
                            "description": "Botun bannerı"
                        }
                    }
                },
                "clear": {
                    "description": "Profil değerlerinin birini veya tamamını varsayılan değere döndür",
                    "name": "temizle",
                    "options": {
                        "value": {
                            "name": "değer",
                            "description": "Sıfırlanacak değer. Eğer boş bırakılırsa bütün değerler sıfırlanır"
                        }
                    }
                }
            }
        },
        "restore": {
            "description": "Bir mesajı Discohook editöründe kurtar",
            "name": "kurtarma",
            "options": {
                "message": {
                    "name": "mesaj",
                    "description": "Kurtarılacak mesaj. Buraya mesaj linki de girilebilir"
                },
                "mode": {
                    "description": "Mesajın nasıl kurtarılacağı. Şu anlık sadece düzenleme seçenekleri kullanılabilir",
                    "name": "mod",
                    "choices": {
                        "edit": "Düzenleme seçenekleriyle",
                        "link": "Gömülü editörü linklemek için"
                    }
                }
            }
        },
        "buttons": {
            "options": {
                "migrate": {
                    "options": {
                        "channel": {
                            "description": "Mesajın bulunduğu kanal (oto-tamamlama sonuçları için)",
                            "name": "kanal"
                        },
                        "message": {
                            "name": "mesaj",
                            "description": "Bu mesajdaki bileşenleri taşıyın. Buraya mesaj linki de girilebilir"
                        }
                    },
                    "name": "taşı",
                    "description": "Bütün eski düğmeleri taşı"
                },
                "add": {
                    "options": {
                        "channel": {
                            "description": "Mesajın bulunduğu kanal (oto-tamamlama sonuçları için)",
                            "name": "kanal"
                        },
                        "message": {
                            "name": "mesaj",
                            "description": "Bu mesaja bir bileşen ekle. Buraya mesaj linki de girilebilir"
                        }
                    },
                    "name": "ekle",
                    "description": "Bileşen ekle"
                },
                "edit": {
                    "options": {
                        "channel": {
                            "description": "Mesajın bulunduğu kanal (oto-tamamlama sonuçları için)",
                            "name": "kanal"
                        },
                        "message": {
                            "name": "mesaj",
                            "description": "Bu mesajdaki bir bileşeni düzenle. Buraya mesaj linki de girilebilir"
                        }
                    },
                    "name": "düzenle",
                    "description": "Bir bileşen düzenle"
                },
                "delete": {
                    "options": {
                        "channel": {
                            "description": "Mesajın bulunduğu kanal (oto-tamamlama sonuçları için)",
                            "name": "kanal"
                        },
                        "message": {
                            "name": "mesaj",
                            "description": "Bu mesajdaki bir bileşeni sil. Buraya mesaj linki de girilebilir"
                        }
                    },
                    "name": "sil",
                    "description": "Bileşen sil"
                }
            },
            "name": "düğmeler",
            "description": "Bileşenleri (düğmeleri/seçimleri) ekle, kaldır ve yönet"
        },
        "reaction-role": {
            "options": {
                "delete": {
                    "options": {
                        "emoji": {
                            "description": "Tepkinin göstereceği emoji. Silme menüsünü görüntülemek için bu seçeneği atla",
                            "name": "emoji"
                        },
                        "message": {
                            "name": "mesaj",
                            "description": "Tepki rolünün silineceği mesaj. Buraya mesaj linki de girilebilir"
                        },
                        "channel": {
                            "name": "kanal",
                            "description": "Mesajın bulunduğu kanal (oto-tamamlama sonuçları için)"
                        }
                    },
                    "name": "sil",
                    "description": "Bir mesajdan bir tepki rolü sil"
                },
                "create": {
                    "options": {
                        "emoji": {
                            "description": "Tepkide gözükecek emoji. Eğer özel emojiler kullanıyorsan tepkiyi sen at",
                            "name": "emoji"
                        },
                        "message": {
                            "name": "mesaj",
                            "description": "Tepki atılacak mesaj. Buraya mesaj linki de girilebilir"
                        },
                        "role": {
                            "name": "rol",
                            "description": "Tepkiye basılınca eklenecek veya çıkarılacak rol"
                        },
                        "channel": {
                            "name": "kanal",
                            "description": "Mesajın bulunduğu kanal (oto-tamamlama sonuçları için)"
                        }
                    },
                    "name": "oluştur",
                    "description": "Yeni tepki rolü oluştur"
                },
                "list": {
                    "options": {
                        "channel": {
                            "description": "Mesajın bulunduğu kanal (oto-tamamlama sonuçları için)"
                        },
                        "message": {
                            "description": "Listelenecek tepki rollerinin olduğu mesaj. Buraya mesaj linki de girilebilir"
                        }
                    },
                    "name": "liste",
                    "description": "Bir mesajdaki bütün tepki rollerini listele"
                }
            },
            "name": "tepki-roller",
            "description": "Tepki rolleri ekle, sil veya yönet"
        },
        "triggers": {
            "options": {
                "add": {
                    "options": {
                        "name": {
                            "description": "Tetikleyicinin ismi",
                            "name": "isim"
                        },
                        "event": {
                            "name": "olay",
                            "description": "Tetikleyiciyi çalıştıracak olay",
                            "choices": {
                                "0": "Üye Katıldı",
                                "1": "Üye Ayrıldı"
                            }
                        }
                    },
                    "name": "ekle",
                    "description": "Yeni tetikleyici ekle"
                },
                "view": {
                    "name": "görüntüleme",
                    "description": "Bir tetikleyiciyi gör ve yönet",
                    "options": {
                        "name": {
                            "name": "isim",
                            "description": "Tetikleyicinin ismi"
                        }
                    }
                }
            },
            "description": "Sunucundaki belirli olaylara yanıt vermesi için tetikleyiciler ekle"
        },
        "help": {
            "options": {
                "mention": {
                    "description": "Eğer başkasına yardım ediyorsan onu bot yanıtlarında mentleyebilirsin",
                    "name": "mention"
                },
                "tag": {
                    "name": "tag",
                    "description": "Yardım tagi"
                }
            },
            "description": "Birçok konu hakkında yardım al"
        },
        "_options": {
            "webhook": {
                "name": "webhook",
                "description": "Hedef webhook"
            },
            "filter-channel": {
                "name": "filtre-kanal",
                "description": "Oto-tamamlanan sonuçların filtreleneceği kanal"
            }
        },
        "deluxe": {
            "name": "deluxe",
            "description": "Deluxe üyeliğinizi senkronize edin",
            "options": {
                "info": {
                    "name": "info",
                    "description": "Premium abonelik sistemimiz olan Discohook Deluxe hakkında bilgi al"
                },
                "sync": {
                    "name": "senkronizasyon",
                    "description": "Deluxe üyeliğinle Discohook websitesinin güncel olduğundan emin ol"
                }
            }
        },
        "format": {
            "name": "format",
            "description": "Kullanıcılar, roller, kanallar ve emojiler için Markdown formatı (biçimlendirmesi) edin",
            "options": {
                "mention": {
                    "name": "mention",
                    "description": "Bir kullanıcı veya rol için ping formatını atar",
                    "options": {
                        "target": {
                            "name": "hedef",
                            "description": "Pinglenecek kullanıcı veya rol"
                        }
                    }
                },
                "channel": {
                    "name": "kanal",
                    "description": "Bir kanal için ping formatını atar",
                    "options": {
                        "target": {
                            "name": "hedef",
                            "description": "Pinglenecek kanal"
                        }
                    }
                },
                "emoji": {
                    "name": "emoji",
                    "description": "Bir sunucu emojisi için kullanım formatını atar",
                    "options": {
                        "target": {
                            "name": "hedef",
                            "description": "Kullanılacak emoji"
                        }
                    }
                }
            }
        },
        "invite": {
            "name": "davet",
            "description": "Bu botun davet URL'si"
        },
        "id": {
            "name": "id",
            "description": "Bir Discord kaynağının sayı ID'sini al",
            "options": {
                "mention": {
                    "name": "mention",
                    "description": "Bir kullanıcının veya rolün ID'sini atar",
                    "options": {
                        "target": {
                            "name": "hedef",
                            "description": "Kullanıcı veya kanal"
                        }
                    }
                },
                "channel": {
                    "name": "kanal",
                    "description": "Bir kanal veya tiradin ID'sini atar",
                    "options": {
                        "target": {
                            "name": "hedef",
                            "description": "Kanal veya tirad"
                        }
                    }
                },
                "emoji": {
                    "name": "emoji",
                    "description": "Bir sunucu emojisinin ID'sini atar",
                    "options": {
                        "target": {
                            "name": "hedef",
                            "description": "Emoji"
                        }
                    }
                }
            }
        },
        "_ctx": {
            "components": {
                "name": "Düğmeler & Bileşenler"
            },
            "edit": {
                "name": "Hızlı Düzenleme"
            },
            "restore": {
                "name": "Kurtarma"
            },
            "webhook": {
                "name": "Webhook Bilgisi"
            },
            "quickedit": {
                "name": "Hızlı Düzenleme"
            },
            "debug": {
                "name": "Hata Ayıklama"
            }
        }
    },
    "noMigratableComponents": "Bu mesajda kayıtlı ve taşınabilir bir bileşen bulunmamaktadır.",
    "noContentAvailable": "Bir içerik yok",
    "noComponentFlow": "Bu bileşen için kayıtlı bir akış bulunmamaktadır. Yeni bir akış ayarlamak için düğmeye tıkla.",
    "noComponentFlowMigratePrompt": "Bu mesajda 5 Eylül 2024'ten önce oluşturulmuş düğmeler varsa, </buttons migrate:908884724087410729> komutunu çalıştırman gerekebilir.",
    "componentWillExpire": "Lütfen düzenlemeyi tamamlayıp bu bileşeni 2 hafta içinde gönder, aksi takdirde taslağın silinecektir.",
    "noTrigger": "Bu sunucuda böyle bir tetikleyici yok.",
    "unnamedTrigger": "İsimsiz tetikleyici",
    "triggerDuplicate": "Bu sunucuda zaten bu olay için bir tetikleyici var.",
    "triggerCreated": "**{{name}}** tetikleyicisi oluşturuldu.",
    "addActions": "Eylem Ekle",
    "noActions": "Eylem yok",
    "manageActions": "Eylemleri Yönet",
    "idUnavailable": "ID mevcut değil.",
    "customize": "Özelleştir",
    "gteNMessagesSent_one": "En az {{count}} mesaj gönderildi",
    "gteNMessagesSent_other": "En az {{count}} messaj gönderildi",
    "webhookDelete": {
        "confirm": "Bu webhooku silmek istediğinden emin misin? Gönderdiği herhangi bir mesajı düzenlemek imkansız olacaktır.",
        "forbidden": "Webhookları yönetme yetkin yok.",
        "wrongServer": "Böyle bir webhook yok ya da bu sunucuda değil.",
        "success": "Webhook başarıyla silindi.",
        "cancel": "Webhook emin ellerde."
    }
}

```

### File: `packages/bot/src/i18n/uk.json`
```json
{
    "commands": {
        "_options": {
            "webhook": {
                "name": "вебхук",
                "description": "Цільовий вебхук"
            },
            "filter-channel": {
                "name": "фільтр-канал",
                "description": "Канал для фільтрації результатів в інших параметрах"
            }
        },
        "buttons": {
            "description": "Додавання, видалення та керування компонентами (кнопки/вибори)",
            "options": {
                "add": {
                    "options": {
                        "message": {
                            "description": "Додати компонент до цього повідомлення. Сюди також можна ввести посилання на повідомлення",
                            "name": "повідомлення"
                        },
                        "channel": {
                            "name": "канал",
                            "description": "Канал у якому це повідомлення, для фільтрації результатів в інших параметрах"
                        }
                    },
                    "name": "додати",
                    "description": "Додати компонент"
                },
                "edit": {
                    "name": "редагувати",
                    "description": "Редагувати компонент",
                    "options": {
                        "message": {
                            "name": "повідомлення",
                            "description": "Відредагувати компонент на цьому повідомленні. Посилання на повідомлення також приймається"
                        },
                        "channel": {
                            "description": "Канал, в якому знаходиться повідомлення, для автозаповнення результатів",
                            "name": "канал"
                        }
                    }
                },
                "delete": {
                    "name": "видалити",
                    "description": "Видалити компонент",
                    "options": {
                        "message": {
                            "name": "повідомлення",
                            "description": "Видалити компонент на цьому повідомленні. Посилання на повідомлення також приймається"
                        },
                        "channel": {
                            "name": "канал",
                            "description": "Канал, в якому знаходиться повідомлення, для автозаповнення результатів"
                        }
                    }
                },
                "migrate": {
                    "name": "перенести",
                    "options": {
                        "message": {
                            "name": "повідомлення",
                            "description": "Перенести елементи цього повідомлення. Можна також вставити посилання на інше повідомлення"
                        },
                        "channel": {
                            "name": "канал",
                            "description": "Канал, в якому знаходиться повідомлення, для автозаповнення результатів"
                        }
                    },
                    "description": "Перенести всі застарілі кнопки"
                }
            },
            "name": "кнопки"
        },
        "deluxe": {
            "options": {
                "info": {
                    "name": "інформація",
                    "description": "Інформація про Discohook Deluxe, нашу преміумпідписку"
                },
                "sync": {
                    "name": "синхронізувати",
                    "description": "Переконайтеся, що вебсайт Discohook оновлено відповідно до вашої Deluxe-підписки"
                }
            },
            "name": "люкс",
            "description": "Синхронізувати вашу підписку Люкс"
        },
        "triggers": {
            "options": {
                "add": {
                    "name": "додати",
                    "description": "Додати новий триґер",
                    "options": {
                        "name": {
                            "name": "ім'я",
                            "description": "Назва триґера"
                        },
                        "event": {
                            "name": "подія",
                            "description": "Подія, яка призведе до спрацьовування триґера",
                            "choices": {
                                "0": "Приєднання учасника",
                                "1": "Видалення учасника"
                            }
                        }
                    }
                },
                "view": {
                    "name": "перегляд",
                    "description": "Переглянути та керувати триґером",
                    "options": {
                        "name": {
                            "name": "назва",
                            "description": "Назва триґера"
                        }
                    }
                }
            },
            "description": "Налаштовує тригери для реагування на події на вашому сервері"
        },
        "webhook": {
            "name": "вебхук",
            "description": "Керування вебхуками",
            "options": {
                "create": {
                    "name": "створити",
                    "description": "Створити вебхук",
                    "options": {
                        "name": {
                            "name": "ім'я",
                            "description": "Ім'я вебхука"
                        },
                        "avatar": {
                            "name": "аватар",
                            "description": "Аватар вебхука"
                        },
                        "channel": {
                            "name": "канал",
                            "description": "Канал у котрому створити вебхук"
                        },
                        "show-url": {
                            "name": "показати-посилання",
                            "description": "Вмикайте це лише якщо вам потрібне посилання для іншого додатку"
                        }
                    }
                },
                "delete": {
                    "name": "видалити",
                    "description": "Видалити вебхук",
                    "options": {
                        "webhook": {
                            "name": "вебхук",
                            "description": "Вебхук котрий видалити"
                        },
                        "filter-channel": {
                            "name": "фільтр-канал"
                        }
                    }
                }
            }
        }
    }
}

```

### File: `packages/bot/src/i18n/zh-CN.json`
```json
{
    "commands": {
        "buttons": {
            "options": {
                "add": {
                    "description": "添加组件",
                    "options": {
                        "message": {
                            "description": "向此消息添加一个组件。这里也接受消息链接",
                            "name": "消息"
                        },
                        "channel": {
                            "name": "频道"
                        }
                    },
                    "name": "添加"
                },
                "delete": {
                    "description": "删除组件",
                    "name": "删除",
                    "options": {
                        "message": {
                            "name": "消息"
                        },
                        "channel": {
                            "name": "频道"
                        }
                    }
                },
                "migrate": {
                    "description": "迁移所有旧版按钮",
                    "name": "迁移",
                    "options": {
                        "message": {
                            "name": "消息"
                        },
                        "channel": {
                            "name": "频道"
                        }
                    }
                },
                "edit": {
                    "description": "编辑一个组件",
                    "name": "编辑",
                    "options": {
                        "message": {
                            "name": "消息"
                        },
                        "channel": {
                            "name": "频道"
                        }
                    }
                }
            },
            "description": "添加、删除和管理组件（按钮/选择界面）",
            "name": "按钮"
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
                            "description": "Webhook 名称",
                            "name": "名称"
                        },
                        "avatar": {
                            "description": "Webhook 的头像"
                        },
                        "channel": {
                            "name": "频道"
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
                            },
                            "name": "事件"
                        },
                        "name": {
                            "name": "名称"
                        }
                    },
                    "name": "添加"
                },
                "view": {
                    "name": "查看",
                    "options": {
                        "name": {
                            "name": "名称"
                        }
                    }
                }
            }
        },
        "deluxe": {
            "options": {
                "sync": {
                    "name": "同步",
                    "description": "确保 Discohook 网站已更新您的 Deluxe 订阅"
                },
                "info": {
                    "name": "信息",
                    "description": "有关 Discohook Deluxe（我们的高级订阅选项）的信息"
                }
            },
            "name": "豪华",
            "description": "同步您的 Deluxe 订阅。"
        },
        "_options": {
            "webhook": {
                "description": "目标 webhook",
                "name": "webhook"
            }
        },
        "welcomer": {
            "options": {
                "set": {
                    "name": "设置",
                    "options": {
                        "channel": {
                            "name": "频道"
                        }
                    }
                },
                "view": {
                    "name": "查看"
                }
            }
        },
        "reaction-role": {
            "name": "身份组",
            "options": {
                "create": {
                    "description": "创建新的身份组",
                    "options": {
                        "message": {
                            "name": "消息"
                        },
                        "channel": {
                            "name": "频道"
                        },
                        "emoji": {
                            "name": "表情符号"
                        }
                    },
                    "name": "创建"
                },
                "delete": {
                    "name": "删除",
                    "options": {
                        "channel": {
                            "name": "频道"
                        },
                        "message": {
                            "name": "消息"
                        },
                        "emoji": {
                            "name": "表情符号"
                        }
                    }
                },
                "list": {
                    "name": "列表"
                }
            },
            "description": "添加、移除和管理身份组"
        },
        "help": {
            "options": {
                "tag": {
                    "name": "标签"
                },
                "mention": {
                    "name": "提及"
                }
            }
        },
        "restore": {
            "name": "恢复",
            "options": {
                "mode": {
                    "name": "模式"
                },
                "message": {
                    "name": "消息"
                }
            }
        },
        "format": {
            "name": "格式",
            "options": {
                "mention": {
                    "name": "提及",
                    "options": {
                        "target": {
                            "name": "目标"
                        }
                    }
                },
                "channel": {
                    "name": "频道",
                    "options": {
                        "target": {
                            "name": "目标"
                        }
                    }
                },
                "emoji": {
                    "name": "表情符号",
                    "options": {
                        "target": {
                            "name": "目标"
                        }
                    }
                }
            }
        },
        "id": {
            "options": {
                "channel": {
                    "options": {
                        "target": {
                            "name": "目标"
                        }
                    },
                    "name": "频道"
                },
                "emoji": {
                    "name": "表情符号",
                    "options": {
                        "target": {
                            "name": "目标"
                        }
                    }
                },
                "mention": {
                    "name": "提及",
                    "options": {
                        "target": {
                            "name": "目标"
                        }
                    }
                }
            }
        },
        "invite": {
            "name": "邀请"
        }
    },
    "addActions": "添加动作",
    "noActions": "没有动作",
    "manageActions": "管理动作",
    "customize": "自定义"
}

```

### File: `packages/bot/src/i18n/zh-TW.json`
```json
{
    "commands": {
        "_options": {
            "webhook": {
                "name": "webhook",
                "description": "目標 Webhook"
            },
            "filter-channel": {
                "description": "用來篩選自動完成結果的頻道",
                "name": "filter-channel"
            }
        },
        "buttons": {
            "name": "buttons",
            "options": {
                "add": {
                    "name": "add",
                    "options": {
                        "message": {
                            "name": "message",
                            "description": "新增元件至此訊息。此處也接受訊息連結"
                        },
                        "channel": {
                            "description": "訊息所在的頻道，用於自動完成結果",
                            "name": "channel"
                        }
                    },
                    "description": "新增元件"
                },
                "edit": {
                    "options": {
                        "message": {
                            "name": "message",
                            "description": "編輯此訊息上的元件。此處也接受訊息連結"
                        },
                        "channel": {
                            "description": "訊息所在的頻道，用於自動完成結果",
                            "name": "channel"
                        }
                    },
                    "description": "編輯元件",
                    "name": "edit"
                },
                "delete": {
                    "name": "delete",
                    "description": "刪除元件",
                    "options": {
                        "message": {
                            "name": "message",
                            "description": "刪除此訊息上的元件。此處也接受訊息連結"
                        },
                        "channel": {
                            "name": "channel",
                            "description": "訊息所在的頻道，用於自動完成結果"
                        }
                    }
                },
                "migrate": {
                    "name": "migrate",
                    "description": "遷移所有舊版按鈕",
                    "options": {
                        "message": {
                            "name": "message",
                            "description": "遷移此訊息上的元件。此處也接受訊息連結"
                        },
                        "channel": {
                            "name": "channel",
                            "description": "訊息所在的頻道，用於自動完成結果"
                        }
                    }
                }
            },
            "description": "新增、移除及管理元件（按鈕／選單）"
        },
        "deluxe": {
            "name": "deluxe",
            "description": "同步你的進階版訂閱",
            "options": {
                "info": {
                    "name": "info",
                    "description": "關於 Discohook 進階版（我們的高級訂閱選項）的資訊"
                },
                "sync": {
                    "name": "sync",
                    "description": "確保 Discohook 網站與你的進階版訂閱保持同步"
                }
            }
        },
        "triggers": {
            "description": "設定觸發器以回應伺服器中的事件",
            "options": {
                "add": {
                    "name": "add",
                    "options": {
                        "name": {
                            "name": "name",
                            "description": "觸發器的名稱"
                        },
                        "event": {
                            "name": "event",
                            "description": "將觸發此觸發器的事件",
                            "choices": {
                                "0": "成員加入",
                                "1": "成員離開"
                            }
                        }
                    },
                    "description": "新增觸發器"
                },
                "view": {
                    "name": "view",
                    "description": "檢視並管理觸發器",
                    "options": {
                        "name": {
                            "name": "name",
                            "description": "觸發器的名稱"
                        }
                    }
                }
            }
        },
        "webhook": {
            "name": "webhook",
            "options": {
                "create": {
                    "name": "create",
                    "description": "建立 Webhook",
                    "options": {
                        "name": {
                            "name": "name",
                            "description": "Webhook 的名稱"
                        },
                        "avatar": {
                            "description": "Webhook 的大頭貼",
                            "name": "avatar"
                        },
                        "channel": {
                            "name": "channel",
                            "description": "建立 Webhook 的頻道"
                        },
                        "show-url": {
                            "name": "show-url",
                            "description": "僅在你需要提供 URL 給外部應用程式時才啟用此選項"
                        }
                    }
                },
                "delete": {
                    "name": "delete",
                    "options": {
                        "webhook": {
                            "name": "webhook",
                            "description": "要刪除的 Webhook"
                        },
                        "filter-channel": {
                            "name": "filter-channel",
                            "description": "用來篩選自動完成結果的頻道"
                        }
                    },
                    "description": "刪除 Webhook"
                },
                "info": {
                    "description": "取得 Webhook 的資訊",
                    "options": {
                        "webhook": {
                            "name": "webhook",
                            "description": "要查詢資訊的 Webhook"
                        },
                        "filter-channel": {
                            "name": "filter-channel",
                            "description": "用來篩選自動完成結果的頻道"
                        },
                        "show-url": {
                            "name": "show-url",
                            "description": "是否跳過「取得 URL」步驟。這會使訊息變為隱藏"
                        }
                    },
                    "name": "info"
                }
            },
            "description": "管理 Webhook"
        },
        "welcomer": {
            "name": "welcomer",
            "description": "設定簡易歡迎功能（另請參閱 /triggers）",
            "options": {
                "set": {
                    "name": "set",
                    "options": {
                        "event": {
                            "name": "event",
                            "choices": {
                                "0": "成員加入（哈囉）",
                                "1": "成員離開（再見）"
                            },
                            "description": "哪個事件應觸發此歡迎功能"
                        },
                        "channel": {
                            "name": "channel",
                            "description": "若未提供 Webhook，則發送訊息的頻道"
                        },
                        "share-link": {
                            "name": "share-link",
                            "description": "訊息使用的分享連結"
                        },
                        "delete-after": {
                            "name": "delete-after",
                            "description": "在刪除訊息前等待的秒數（0 表示永不刪除）"
                        },
                        "webhook": {
                            "name": "webhook",
                            "description": "用來發送訊息的 Webhook"
                        }
                    },
                    "description": "設定新的歡迎功能或覆蓋現有設定"
                },
                "view": {
                    "description": "檢視目前歡迎功能設定的摘要",
                    "options": {
                        "event": {
                            "name": "event",
                            "description": "歡迎功能的事件"
                        }
                    },
                    "name": "view"
                },
                "delete": {
                    "name": "delete",
                    "options": {
                        "event": {
                            "name": "event",
                            "description": "歡迎功能的事件"
                        }
                    },
                    "description": "刪除歡迎功能設定"
                }
            }
        },
        "profile": {
            "name": "profile",
            "description": "設定 Discohook Utils 在伺服器中的個人檔案",
            "options": {
                "set": {
                    "options": {
                        "name": {
                            "name": "name",
                            "description": "機器人的暱稱"
                        },
                        "avatar": {
                            "name": "avatar",
                            "description": "機器人的大頭貼"
                        },
                        "banner": {
                            "name": "banner",
                            "description": "機器人的橫幅"
                        }
                    },
                    "name": "set",
                    "description": "以自訂值覆蓋機器人的暱稱、大頭貼或橫幅"
                },
                "clear": {
                    "name": "clear",
                    "description": "將一個或全部個人檔案值重設為預設值",
                    "options": {
                        "value": {
                            "name": "value",
                            "description": "要重設的值。若未提供，則清除所有值"
                        }
                    }
                }
            }
        },
        "help": {
            "description": "取得各種主題的幫助",
            "options": {
                "tag": {
                    "name": "tag",
                    "description": "要取得幫助的標籤"
                },
                "mention": {
                    "name": "mention",
                    "description": "若你正在協助他人，在機器人回覆中提及對方"
                }
            }
        },
        "reaction-role": {
            "name": "reaction-role",
            "description": "新增、移除及管理反應身分組",
            "options": {
                "create": {
                    "name": "create",
                    "description": "建立新的反應身分組",
                    "options": {
                        "message": {
                            "description": "要建立反應的訊息。此處也接受訊息連結",
                            "name": "message"
                        },
                        "emoji": {
                            "name": "emoji",
                            "description": "反應應顯示的表情符號。若為外部表情符號，請在機器人之前先反應"
                        },
                        "role": {
                            "name": "role",
                            "description": "點擊反應時應授予／移除的身分組"
                        },
                        "channel": {
                            "name": "channel",
                            "description": "訊息所在的頻道，用於自動完成結果"
                        }
                    }
                },
                "delete": {
                    "name": "delete",
                    "description": "從訊息中刪除反應身分組",
                    "options": {
                        "emoji": {
                            "name": "emoji",
                            "description": "反應顯示的表情符號。省略此參數可查看刪除選單"
                        },
                        "channel": {
                            "name": "channel",
                            "description": "訊息所在的頻道，用於自動完成結果"
                        },
                        "message": {
                            "description": "要刪除反應身分組的訊息。此處也接受訊息連結",
                            "name": "message"
                        }
                    }
                },
                "list": {
                    "options": {
                        "message": {
                            "description": "要列出反應身分組的訊息。此處也接受訊息連結"
                        },
                        "channel": {
                            "description": "訊息所在的頻道，用於自動完成結果"
                        }
                    },
                    "description": "列出訊息上的所有反應身分組",
                    "name": "list"
                }
            }
        },
        "restore": {
            "name": "restore",
            "description": "將訊息還原至 Discohook 編輯器",
            "options": {
                "message": {
                    "description": "要還原的訊息。此處也接受訊息連結",
                    "name": "message"
                },
                "mode": {
                    "name": "mode",
                    "choices": {
                        "edit": "含編輯選項",
                        "link": "至連結嵌入編輯器"
                    },
                    "description": "還原訊息的方式。目前僅支援包含編輯選項"
                }
            }
        },
        "format": {
            "name": "format",
            "options": {
                "mention": {
                    "name": "mention",
                    "description": "輸出使用者或身分組的提及格式",
                    "options": {
                        "target": {
                            "name": "target",
                            "description": "要提及的使用者或身分組"
                        }
                    }
                },
                "channel": {
                    "description": "輸出頻道的提及格式",
                    "options": {
                        "target": {
                            "name": "target",
                            "description": "要提及的頻道"
                        }
                    },
                    "name": "channel"
                },
                "emoji": {
                    "name": "emoji",
                    "description": "輸出伺服器表情符號的使用格式",
                    "options": {
                        "target": {
                            "name": "target",
                            "description": "要使用的表情符號"
                        }
                    }
                }
            },
            "description": "取得使用者、身分組、頻道和表情符號的 Markdown 格式"
        },
        "invite": {
            "name": "invite",
            "description": "此機器人的邀請連結"
        },
        "id": {
            "name": "id",
            "options": {
                "mention": {
                    "name": "mention",
                    "description": "輸出使用者或身分組的 ID",
                    "options": {
                        "target": {
                            "description": "使用者或身分組",
                            "name": "target"
                        }
                    }
                },
                "channel": {
                    "name": "channel",
                    "description": "輸出頻道或討論串的 ID",
                    "options": {
                        "target": {
                            "name": "target",
                            "description": "頻道或討論串"
                        }
                    }
                },
                "emoji": {
                    "name": "emoji",
                    "options": {
                        "target": {
                            "name": "target",
                            "description": "表情符號"
                        }
                    },
                    "description": "輸出伺服器表情符號的 ID"
                }
            },
            "description": "取得 Discord 資源的數字 ID"
        },
        "_ctx": {
            "edit": {
                "name": "快速編輯"
            },
            "restore": {
                "name": "還原"
            },
            "webhook": {
                "name": "Webhook 資訊"
            },
            "debug": {
                "name": "偵錯"
            },
            "components": {
                "name": "按鈕與元件"
            },
            "quickedit": {
                "name": "快速編輯"
            }
        }
    },
    "noMigratableComponents": "此訊息沒有已註冊、可遷移的元件。",
    "noContentAvailable": "無可用內容",
    "componentWillExpire": "請在 2 週內完成編輯並提交此元件，否則草稿將被刪除。",
    "noTrigger": "此伺服器沒有該名稱的觸發器。",
    "unnamedTrigger": "未命名觸發器",
    "addActions": "新增動作",
    "noActions": "無動作",
    "manageActions": "管理動作",
    "idUnavailable": "ID 無法取得。",
    "customize": "自訂",
    "gteNMessagesSent_one": "至少已發送 {{count}} 則訊息",
    "webhookDelete": {
        "forbidden": "你沒有管理 Webhook 的權限。",
        "wrongServer": "Webhook 不存在或不在此伺服器中。",
        "success": "已成功刪除 Webhook。",
        "cancel": "Webhook 安然無恙。",
        "confirm": "你確定要刪除此 Webhook 嗎？這將使所有透過它發送的訊息無法再被編輯。"
    },
    "gteNMessagesSent_other": "至少已發送 {{count}} 則訊息",
    "noComponentFlow": "此元件未註冊任何流程。點擊按鈕以設定新流程。",
    "triggerDuplicate": "此伺服器已有該事件的觸發器。",
    "triggerCreated": "觸發器 **{{name}}** 建立成功。",
    "noComponentFlowMigratePrompt": "如果此訊息包含 2024 年 9 月 5 日前的按鈕，你可能需要執行 </buttons migrate:908884724087410729>。"
}

```

