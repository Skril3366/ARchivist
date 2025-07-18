# Telegram JSON Chat Export Format – Single Chat Version

Exported using: Telegram Desktop's "Export Chat History" functionality with "Export as JSON" option
Location: The JSON file is typically named result.json and is accompanied by separate folders for media content (e.g., photos, files, videos)

## Top-Level Structure

For a single-chat export, the root of the JSON document is a single JSON object representing the exported chat. There is no chats wrapper or chat list.

### Root-Level Fields

| Field      | Type     | Description                                                         | Required | Possible Values / Notes                                   |
|------------|----------|---------------------------------------------------------------------|----------|-----------------------------------------------------------|
| name       | string   | The name of the contact, group, or channel                          | Yes      | Contact name, group title, or channel title               |
| type       | string   | Type of chat                                                        | Yes      | `"personal_chat"`, `"private_group"`, `"channel"`         |
| id         | number   | Internal Telegram chat identifier                                   | Yes      | Numeric unique chat ID                                    |
| messages   | array    | Ordered list of message objects                                     | Yes      | Array, sorted by message ID and/or date                   |

## Message Structure

Each item in the messages array is a message object. Messages are either normal user messages or service/system messages (e.g., join/leave events, pinning, etc.).

### Common Fields

| Field             | Type              | Description                                                              | Required | Notes                                                                 |
|------------------|-------------------|--------------------------------------------------------------------------|----------|----------------------------------------------------------------------|
| id               | number            | Unique message ID within the chat                                        | Yes      | Monotonically increasing integer                                      |
| type             | string            | Type of message                                                          | Yes      | Allowed values: `"message"`, `"service"`                             |
| date             | string            | ISO 8601 UTC datetime string                                             | Yes      | Format: `YYYY-MM-DDTHH:MM:SS`                                        |
| date_unixtime    | string            | Unix timestamp (as string)                                               | Yes      | Same time as `date`, represented in Unix epoch seconds               |

### Optional Fields (Commonly Used)

| Field                | Type               | Description                                                         | Required | Conditions / Notes                                                   |
|---------------------|--------------------|---------------------------------------------------------------------|----------|---------------------------------------------------------------------|
| from                | string             | Display name of the sender (contact/group member)                   | No       | Omitted for deleted users or anonymous posts                        |
| from_id             | string or number   | Telegram user, bot, or channel ID                                   | Yes      | Format typically `user12345678`, but may be numeric                 |
| reply_to_message_id | number             | ID of the referenced message (in a reply)                           | No       | Only present for reply messages                                     |
| forwarded_from      | string             | Display name of original sender                                     | No       | Present for forwarded messages only                                 |
| forwarded_from_id   | string             | ID or username of original sender                                   | No       | Can be user ID or channel ID                                        |
| edited              | string             | ISO 8601 datetime when message was edited                           | No       | Present if the message was edited                                   |
| edited_unixtime     | string             | Unix timestamp of edit                                              | No       | Present if message was edited                                       |
| text                | string or array    | The actual message content                                           | Yes      | Plain text string or structured array (see Text Entities section)   |
| text_entities       | array              | Styling and entity ranges for text                                   | No       | Only used for messages with styling or hyperlinks                   |
| file                | string             | Relative path to file attachment                                     | No       | Refers to media file (e.g., files/file_1.mp4)                        |
| mime_type           | string             | MIME type of attached file                                           | No       | Provided if `file` is present                                       |
| photo               | string             | Relative path to photo media file                                    | No       | For photo messages                                                   |
| width, height       | number             | Dimensions of attached photo                                         | No       | Only for image/photo messages                                       |

## Text Field (Plain and Formatted)

The message text field can be represented in two formats:

### Plain String

```json
"text": "Hello world"
```

### Structured Array (Formatted Text)

```json
"text": [
  "This is ",
  { "type": "bold", "text": "bold" },
  " and ",
  { "type": "italic", "text": "italic" },
  "."
]
```

### Text Entities

When the content requires rich formatting, hyperlinks, or mentions, it is accompanied by the optional text_entities field:

| Field    | Type   | Description                                  | Required | Possible Values for type                  |
|----------|--------|----------------------------------------------|----------|-------------------------------------------|
| type     | string | Type of formatting or semantic entity       | Yes      | `"plain"`, `"bold"`, `"italic"`, `"code"`, `"pre"`, `"url"`, `"mention"`, `"hashtag"`, `"underline"` |
| text     | string | The actual content                          | Yes      | Text to be rendered with the given style  |
| href     | string | URL for link entities                       | No       | Present only if type is `"url"`           |

Note: text_entities and formatted array text content may describe the same structure.

## Service Messages

Service messages include group events, user invites, leaves, pinned messages, and other non-user content. These have a different set of fields.

### Additional Fields for type: "service"

| Field       | Type     | Description                                      | Required | Conditions |
|-------------|----------|--------------------------------------------------|----------|------------|
| actor       | string   | Display name of the user who performed the action | Yes      | —          |
| actor_id    | string   | ID of the actor (in the form `user12345678`)      | Yes      | —          |
| action      | string   | Type of action that occurred                      | Yes      | See possible values below |
| members     | array    | Affected users (for member-related actions)       | No       | Required for `invite_members`            |

#### Allowed Values for field: action

| Action Value       | Description                                   |
|--------------------|-----------------------------------------------|
| "invite_members"   | One or more users were added to the group     |
| "photo_changed"    | Group or channel photo was updated            |
| "title_changed"    | Group or channel title was changed            |
| "left_group"       | A user left the group                         |
| "pin_message"      | A message was pinned to the top               |
| "create_group"     | Group was created                             |
| "create_channel"   | Channel was created                           |

## Example: Standard Message

```json
{
  "id": 100,
  "type": "message",
  "date": "2023-07-01T09:00:00",
  "date_unixtime": "1688192400",
  "from": "Alice",
  "from_id": "user12345678",
  "text": "Hello, world!"
}
```

## Example: Message With Media and Styled Text

```json
{
  "id": 101,
  "type": "message",
  "date": "2023-07-01T09:05:00",
  "date_unixtime": "1688192700",
  "from": "Bob",
  "from_id": "user87654321",
  "photo": "photos/photo_1@2023-07-01_09-05-00.jpg",
  "width": 800,
  "height": 600,
  "text": [
    "Here is a ",
    { "type": "bold", "text": "photo" },
    " from my trip"
  ]
}
```

## Example: Service Message

```json
{
  "id": 150,
  "type": "service",
  "date": "2023-07-01T09:15:00",
  "date_unixtime": "1688193300",
  "actor": "Alice",
  "actor_id": "user12345678",
  "action": "invite_members",
  "members": ["Bob", "Charlie"]
}
```

## Notes

- Fields not applicable to a message are omitted—not present as null.
- Media files (e.g., photos, videos) are saved in folders relative to the JSON and referenced by filename only.
- Telegram does not export metadata such as message read status, reactions, replies threading (beyond message ID), nor delivery indicators.
- Deleted messages are not included in the export; deleted users or bots may appear with null `from` field.

## Summary of Field Types

| Field                 | Type            |
|----------------------|-----------------|
| id                   | number           |
| type                 | string           |
| date                 | string (ISO 8601) |
| date_unixtime        | string           |
| from                 | string           |
| from_id              | string or number |
| text                 | string or array  |
| text_entities        | array            |
| file                 | string           |
| mime_type            | string           |
| photo                | string           |
| width, height        | number           |
| reply_to_message_id  | number           |
| forwarded_from       | string           |
| forwarded_from_id    | string           |
| edited               | string (ISO 8601) |
| edited_unixtime      | string           |
| actor                | string           |
| actor_id             | string           |
| action               | string           |
| members              | array (strings)  |

This technical specification covers all major aspects of single-chat Telegram
JSON file exports and should enable accurate parsing, transformation, or
analysis of exported chat content.
