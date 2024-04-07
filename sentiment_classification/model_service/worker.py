import pika, json, torch
import logging
from app.model import classifier, vectorizer, create_mask

FORMAT = ('%(asctime)-15s %(threadName)-15s'
          ' %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(level=logging.INFO,
                    filename='worker.log',
                    format=FORMAT,
                    filemode='a')
log = logging.getLogger()
log.setLevel(logging.INFO)

classifier.load_state_dict(
    torch.load('./app/model/transformer_sentiment_classifier.pt', map_location=torch.device('cpu')))
classifier.eval()

target_dict = dict()
for i in range(vectorizer.category_vocab.__len__()):
    target_dict[i] = vectorizer.category_vocab.lookup_index(i)

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='rpc_queue')


def predict(body):
    vectorized_text = torch.Tensor(vectorizer.vectorize(body)['source_vector']).unsqueeze(0).long()

    src_mask, src_padding_mask = create_mask(vectorized_text)
    y_pred = classifier(vectorized_text, src_padding_mask=src_padding_mask, src_mask=src_mask)
    _, pred_index = y_pred.max(dim=1)

    predicted_category = target_dict[pred_index.item()]

    return predicted_category


def on_request(ch, method, props, body):
    print('got request: ', body.decode('UTF-8'))
    log.info('got request: %s', body.decode('UTF-8'))
    result = predict(body.decode('UTF-8'))
    ch.basic_publish(exchange='', routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id=props.correlation_id),
                     body=json.dumps(result))
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='rpc_queue', on_message_callback=on_request)

print(" [x] Awaiting RPC requests")
log.info('[x] Awaiting RPC requests')
channel.start_consuming()
