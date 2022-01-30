# QDrant Celebrity Voice Similarity

## Tutorial
1. Make sure that you have `docker` and `docker-compose` installed on your computer.
2. Download [The VoxCeleb1 Dataset](https://www.robots.ox.ac.uk/~vgg/data/voxceleb/vox1.html). Place it in the root repository folder, s.t. your directory tree would like like that: 
- ./voxceleba1/id10001
- ./voxceleba1/id10002
- ...
- ./bot.py
- ./query.py
- And so on
3. Create QDrant collection. This step can be omitted if you have already done that or downloaded an existing vector collection for QDrant. To do that from scratch, use the following commands:
```
# (Optional) Create virtual environment 
$ python -m venv venv && source venv/bin/activate

# Install all the dependencies
$ pip install -r requirements.txt

# Run QDrant inside Docker container
$ docker run -p 6333:6333 -v $(pwd)/qdrant_data:/qdrant/storage generall/qdrant

# Run script for creating the vector database
$ python create_qdrant_dataset.py
```
These steps will produce a folder name `qdrant_data` in the root of the repository which contains all the required data for QDrant.

4. Create YAML config file inside the root repository directory for the bot configuration. Create it with the name `cfg.yaml` and with the following content:
```
API_KEY: YOUR_KEY
collection_name: test_collection
log_file: log.txt
```
Replace `YOUR_KEY` with the actual key that Telegram @BotFather gave you. For more details, please read some guide about Telegram bots.

5. Run the docker-compose command to build and run all the required containers together:
```
docker-compose up
```
6. Open your Telegram bot and try it! It should work.