FROM public.ecr.aws/lambda/python:3.11

# Install dependencies
COPY aws/lambda/requirements_ml.txt ${LAMBDA_TASK_ROOT}
RUN pip install --upgrade pip && \
    pip install -r requirements_ml.txt

# Copy logic
COPY aws/lambda/stock_screener_handler.py ${LAMBDA_TASK_ROOT}
COPY aws/lambda/ml_trainer_handler.py ${LAMBDA_TASK_ROOT}

# Copy src modules
COPY src/ ${LAMBDA_TASK_ROOT}/src/

# Command to run the handler
CMD [ "stock_screener_handler.lambda_handler" ]
