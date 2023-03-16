#!/bin/bash

mongorestore mongodb://root:example@127.0.0.1:27017/?authSource=admin --dir /dump
