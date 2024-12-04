#!/usr/bin/env bash

docker-compose -f "$SERVICES_PATH/catchme/docker-compose.yml" up -d --build