# REN Facade Sorter Bot

A Telegram bot designed to streamline the process of uploading and organizing facade photos of buildings during inspections. The bot provides an intuitive interface for categorizing photos by inspection type, building block, orientation, and floor level, automatically saving them to a structured folder hierarchy.

## 🎯 Purpose

This bot is specifically designed for building facade inspections, allowing users to:
- Upload photos systematically during building inspections
- Automatically organize photos into a structured folder system
- Support multiple inspection types (BW and SR)
- Handle different building blocks and orientations
- Manage photos across multiple floor levels
- Provide visual building scheme references during the selection process

## ✨ Features

- **Interactive Selection Process**: Step-by-step guided photo categorization
- **Visual Building Schemes**: Display building layout images during selection
- **Batch Photo Upload**: Support for single photos and media groups
- **Document Support**: Handle both compressed photos and uncompressed image files
- **Automatic File Organization**: Creates structured folder hierarchy automatically
- **FSM State Management**: Maintains user session state throughout the process
- **Progress Tracking**: Real-time upload progress for multiple files
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Logging**: Detailed logging for monitoring and debugging

## 🏗️ How It Works

### User Flow
1. **Start**: User sends `/start` command and sees building scheme
2. **Inspection Selection**: Choose between BW or SR inspection types
3. **Block Selection**: Select building block (A or B)
4. **Orientation Selection**: Choose cardinal direction (East, North, South, West) or courtyard orientation
5. **Level Selection**: Pick floor level (GF or L1-L11)
6. **Confirmation**: Review selected parameters
7. **Photo Upload**: Send photos (single or multiple)
8. **Auto-Save**: Photos are automatically saved to structured folders
9. **Continue**: Option to upload more photos or start new location

### File Organization Structure
Photos are saved following this hierarchy:
```
structure_inspections/
├── BW/                          # Inspection Type
│   ├── A/                       # Building Block
│   │   ├── GF/                  # Floor Level
│   │   │   ├── East/            # Orientation
│   │   │   │   └── unsorted/    # Photos folder
│   │   │   ├── North/
│   │   │   │   └── unsorted/
│   │   │   └── Courtyard_North/
│   │   │       └── unsorted/
│   │   └── L1/
│   │       └── East/
│   │           └── unsorted/
│   └── B/
│       └── GF/
│           └── East/
│               └── unsorted/
└── SR/
    └── A/
        └── GF/
            └── East/
                └── unsorted/
```

### Example Paths
- BW inspection, Block A, East orientation, Level 5: `structure_inspections/BW/A/L5/East/unsorted/`
- SR inspection, Block A, Courtyard North, Ground Floor: `structure_inspections/SR/A/GF/Courtyard_North/unsorted/`
- SR inspection, Block B, East orientation, Ground Floor: `structure_inspections/SR/B/GF/East/unsorted/`

## 🏛️ Project Architecture

### File Structure
```
REN_Facade_Sorter/
├── main.py                      # Entry point
├── config.py                    # Configuration settings
├── requirements.txt             # Python dependencies
├── .env.example                # Environment variables template
├── logs/                       # Log files directory
├── structure_inspections/      # Photo storage directory
│   ├── BW/                     # BW inspection photos
│   └── SR/                     # SR inspection photos
└── app/                        # Main application package
    ├── __init__.py
    ├── messages.py             # Bot text messages and constants
    ├── assets/                 # Static assets
    │   └── images/
    │       └── scheme/         # Building scheme images
    │           ├── README.md
    │           ├── scheme.png              # General building scheme
    │           ├── scheme_block_A.png      # Block A detailed scheme
    │           └── scheme_block_B.png      # Block B detailed scheme
    ├── handlers/               # Message and callback handlers
    │   ├── __init__.py         # Handler registration
    │   ├── start.py            # /start, /help, /cancel commands
    │   ├── callbacks.py        # Inline button callbacks
    │   └── photos.py           # Photo upload handling
    ├── keyboards/              # Telegram inline keyboards
    │   ├── __init__.py
    │   └── inline.py           # Dynamic inline keyboards
    ├── states/                 # FSM state definitions
    │   └── __init__.py         # PhotoUploadStates class
    ├── services/               # Business logic services
    └── utils/                  # Utility modules
        └── logger.py           # Logging configuration
```

### Key Components

#### 1. **Entry Point** (`main.py`)
- Initializes the async Telegram bot
- Configures FSM storage (Memory or Redis)
- Registers all handlers
- Starts infinity polling

#### 2. **Configuration** (`config.py`)
- Pydantic-based settings management
- Environment variable loading
- Type validation and defaults

#### 3. **State Management** (`app/states/`)
- FSM states for guided user flow:
  - `selecting_parameters`: Initial parameter selection
  - `selecting_level`: Floor level selection
  - `confirming_selection`: Parameter confirmation
  - `waiting_for_photos`: Photo upload state

#### 4. **Handlers** (`app/handlers/`)
- **Start Handler**: Commands (`/start`, `/help`, `/cancel`)
- **Callback Handler**: Inline button interactions
- **Photo Handler**: Photo and document upload processing

#### 5. **Keyboards** (`app/keyboards/`)
- Dynamic inline keyboards with radio button logic
- Context-aware button states
- Multi-step navigation support

#### 6. **Utilities** (`app/utils/`)
- Structured logging with Loguru
- File rotation and compression
- Console and file output

## 📚 Libraries Used

### Core Dependencies
- **`pytelegrambotapi`**: Telegram Bot API wrapper with async support
- **`aiohttp`**: Async HTTP client for Telegram API calls
- **`pydantic`**: Data validation and settings management
- **`pydantic-settings`**: Environment-based configuration
- **`python-dotenv`**: Environment variable loading
- **`loguru`**: Advanced logging with rotation and formatting

### Optional Dependencies
- **`redis>=5.0.0`**: Redis storage for FSM state persistence (commented out by default)

### Built-in Libraries
- **`asyncio`**: Asynchronous programming support
- **`os`**: File system operations
- **`datetime`**: Timestamp generation
- **`typing`**: Type hints and annotations

## 🚀 Setup Instructions

### 1. Clone and Navigate
```bash
cd bots/REN_Facade_Sorter
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Configure the following variables in `.env`:

#### Required Settings
```env
# Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Logging Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Photo Storage Path (absolute or relative path)
INSPECTIONS_BASE_PATH=/path/to/structure_inspections
```

#### Optional Redis Settings (for persistent FSM storage)
```env
# Redis Configuration (uncomment to enable)
# REDIS_HOST=localhost
# REDIS_PORT=6379
# REDIS_PASSWORD=your_redis_password
# REDIS_DB=0
```

### 5. Obtain Telegram Bot Token

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Create new bot with `/newbot`
3. Copy the provided token to your `.env` file

### 6. Add Building Scheme Images

Place building scheme images in `app/assets/images/scheme/`:
- `scheme.png`: General building layout (shown at start)
- `scheme_block_A.png`: Block A detailed scheme (shown during level selection)
- `scheme_block_B.png`: Block B detailed scheme (shown during level selection)

**Image Requirements:**
- Format: PNG
- Recommended size: 800x600 pixels
- Content: Clear orientation markings (East, North, South, West, Courtyard directions)

### 7. Run the Bot
```bash
python main.py
```

The bot will start and display:
```
Starting REN Facade Sorter bot with Memory FSM...
```

## 🔄 Redis Storage Configuration

By default, the bot uses **Memory storage** for FSM states, which means all user states are lost when the bot restarts. For production environments or when you need persistent state management, you can switch to **Redis storage**.

### Benefits of Redis Storage
- **State Persistence**: User sessions survive bot restarts
- **Scalability**: Support for multiple bot instances
- **Reliability**: Prevents data loss during deployments
- **Performance**: Efficient state management for high-traffic bots

### Enabling Redis Storage

#### 1. Install Redis Server
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install redis-server

# macOS
brew install redis

# Docker
docker run -d --name redis -p 6379:6379 redis:latest
```

#### 2. Update Dependencies
Uncomment the Redis dependency in `requirements.txt`:
```txt
# Cache and FSM
redis>=5.0.0
```

Then install:
```bash
pip install redis>=5.0.0
```

#### 3. Configure Environment Variables
Uncomment and configure Redis settings in your `.env`:
```env
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_password_if_needed
REDIS_DB=0
```

#### 4. Update Configuration
Uncomment Redis settings in `config.py`:
```python
REDIS_HOST: str = Field("localhost", description="Redis host")
REDIS_PORT: int = Field(6379, description="Redis port")
REDIS_DB: int = Field(0, description="Redis database number")
REDIS_PASSWORD: Optional[str] = Field(None, description="Redis password (optional)")
```

#### 5. Switch Storage in main.py
Comment out Memory storage and uncomment Redis storage:
```python
# FSM storage (Memory) - Comment this out
# storage = StateMemoryStorage()

# FSM storage (Redis) - Uncomment this
storage = StateRedisStorage(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    prefix='ren_facade_sorter_bot_'
)
```

#### 6. Restart the Bot
```bash
python main.py
```

The bot will now display:
```
Starting REN Facade Sorter bot with Redis FSM...
```

### Redis Storage Features
- **Automatic State Persistence**: All user selections and states are preserved
- **Graceful Restarts**: Users can continue where they left off after bot restarts
- **Data Isolation**: Uses prefixed keys (`ren_facade_sorter_bot_`) to avoid conflicts
- **Configurable Database**: Separate Redis database for the bot data

## 🎮 Bot Commands

- **`/start`**: Initialize bot and begin photo upload process
- **`/help`**: Display help information and usage instructions
- **`/cancel`**: Cancel current operation and reset user state

## 📝 Usage Example

1. **Start the bot**: Send `/start`
2. **Select inspection**: Choose "BW" or "SR"
3. **Choose block**: Select "A" or "B"
4. **Pick orientation**: Choose "East", "North", "South", "West", or courtyard direction
5. **Select level**: Choose "GF" or "L1" through "L11"
6. **Confirm**: Review your selections
7. **Upload photos**: Send one or multiple photos
8. **Continue**: Add more photos or start a new location

## 🔧 Development

### Adding New Features
- **Handlers**: Add new message handlers in `app/handlers/`
- **States**: Define new FSM states in `app/states/`
- **Keyboards**: Create new inline keyboards in `app/keyboards/`
- **Messages**: Add text constants in `app/messages.py`

### Logging
Logs are automatically created in the `logs/` directory with:
- **Console output**: Colored, human-readable format
- **File output**: Structured format with rotation (10MB max)
- **Log retention**: 10 days with compression

### Error Handling
The bot includes comprehensive error handling:
- **File upload errors**: Graceful handling with user notification
- **State validation**: Ensures all required parameters are selected
- **Network errors**: Automatic retry mechanisms
- **Invalid inputs**: User-friendly error messages

## 🤝 Contributing

1. Follow the existing code structure and patterns
2. Add appropriate error handling and logging
3. Update documentation for new features
4. Test with both Memory and Redis storage configurations
5. Ensure all text messages are defined in `app/messages.py`

## 📞 Support

For issues or questions:
1. Check the logs in `logs/bot.log`
2. Verify your `.env` configuration
3. Ensure all required dependencies are installed
4. Confirm building scheme images are properly placed

---

**Note**: This bot is specifically designed for the REN building facade inspection workflow. The folder structure and inspection types (BW/SR) are tailored to this specific use case. 