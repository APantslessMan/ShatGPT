# ShatGPT Discord Bot

ShatGPT is a Discord bot powered by OpenAI's GPT models, designed to provide a unique and entertaining interaction experience for users. The bot features a grumpy personality and offers various functionalities including study room management and question answering.

## Features

- **Personalized AI Responses**: Utilizes OpenAI's GPT models to generate responses with a customizable personality.
- **Study Room Management**: Create, list, and remove study rooms within a Discord server.
- **User Interaction**: Responds to various commands including greetings and question answering.
- **Database Integration**: Uses SQLite to store information about study rooms, users, and bot preferences.

## Discord Server Setup

[Placeholder: Add instructions for setting up the Discord server, including creating necessary categories, setting permissions, and any other preparations required before adding the bot.]

## Commands

- `!hello`: Greets the user.
- `!ask [question]`: Asks ShatGPT a question.
- `!primedirective`: Displays the bot's current personality setting.
- `!set_personality`: (Admin only) Updates the bot's personality.

### Study Room Functionality

ShatGPT offers a comprehensive study room management system:

- `!sr <room_name>`: Creates a new study room.
  - Example: `!sr calculus` creates a room named #calculus under the //STUDYROOMS category.
  - Limited to 4 rooms per user.
  - Room names are automatically formatted (lowercase, spaces replaced with hyphens).

- `!lr`: Lists all existing study rooms.

- `!rc <room_name>`: Removes a specified study room.
  - Only the creator or an admin can remove a room.

#### Study Room Tutorial:

1. Create a room: 
   ```
   User: !sr Advanced Physics
   Bot: Created study room #advanced-physics. You have 3 rooms left.
   ```

2. List rooms:
   ```
   User: !lr
   Bot: Current study rooms:
        - #advanced-physics (created by @User1)
        - #machine-learning (created by @User2)
   ```

3. Remove a room:
   ```
   User: !rc advanced-physics
   Bot: Study room #advanced-physics has been removed.
   ```

Study rooms appear as text channels under the //STUDYROOMS category, allowing focused discussions on specific topics.

## Setup

1. Clone the repository.
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   - `DISCORD_TOKEN`: Your Discord bot token
   - `OPENROUTER_API_KEY`: Your OpenAI API key
   - `OPENAI_BASE_URL`: The base URL for OpenAI API

4. Run the bot:
   ```
   python main.py
   ```

## Docker Support

The project includes a Dockerfile for containerization. To build and run the Docker image:

```
docker build -t shatgpt .
docker run shatgpt
```

## Deployment

The project includes a GitHub Actions workflow for automatic deployment to Docker Hub. Ensure you have set the following secrets in your GitHub repository:

- `DOCKER_USERNAME`: Your Docker Hub username
- `DOCKER_PASSWORD`: Your Docker Hub password

## Database

The bot uses SQLite for data persistence. The database file `shatgpt.db` will be created automatically when the bot runs.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Insert your chosen license here]