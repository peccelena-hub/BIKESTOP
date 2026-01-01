FROM python:3.11-slim
WORKDIR /app
COPY backend ./backend
COPY frontend ./frontend
CMD ["python","-c","print('BikeStop placeholder backend/frontend')"]
