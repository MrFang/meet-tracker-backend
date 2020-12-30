docker build -t $1 .
docker run -p 0.0.0.0:$2:8000 --name $1 -v "$(pwd)"/dist:/usr/src/app/dist:ro -d $1