#!/bin/bash
cd /home/runner/workspace/backend && python main.py &
sleep 2
cd /home/runner/workspace/frontend && npm run dev
