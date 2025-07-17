#!/bin/bash
wget https://your-cloud-storage-link/model.h5 -O model.h5
uvicorn app:app --host=0.0.0.0 --port=10000
