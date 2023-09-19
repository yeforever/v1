docker stop $(docker ps -a | grep "brief" | awk '{print $1}')
docker rm $(docker ps -a | grep "brief" | awk '{print $1}')
sh build.sh
sh start_contain.sh
docker images|grep none|awk '{print $3 }'|xargs docker rmi