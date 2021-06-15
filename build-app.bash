cd client
npm install && npm run build

cd ..
mkdir -p ./server/static && rm -rf ./server/static/* && cp -rf ./client/dist/* ./server/static

cd server
pip install -r requirements.txt