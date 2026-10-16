import telebot
from keras.models import load_model  # TensorFlow is required for Keras to work
from PIL import Image, ImageOps  # Install pillow instead of PIL
import numpy as np


bot = telebot.TeleBot("8201752628:AAFk4hL-Eek_14k1iq7Or34ebs_F5o5nhnk")
    
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Здравствуйте! Я ваш Telegram бот. Отправьте мне фото эмблемы производителя авто (/help, если не получается определить фото)")

@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.reply_to(message, "Здравствуйте! Это вспомогательное сообщение. Вот инструкция по использованию бота:" \
    "1. Включите камеру на телефоне" \
    "2. Поднесите телефон к эмблеме на расстояние 10 - 20 см" \
    "3. Сфотографируйте логотип" \
    "4. Следите, чтобы фото было качественным" \
    "5. отправьте фото боту." \
    "Бот должен вывести название автопроизводителя. Если этого не произойдет, возможно он еще не знает эту марку.")

def get_class(image_path):
    # Disable scientific notation for clarity
    np.set_printoptions(suppress=True)
    
    model = load_model("keras_model.h5", compile=False)
    class_names = open("labels.txt", "r").readlines()
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

    # Replace this with the path to your image
    image = Image.open(image_path).convert("RGB")

    # resizing the image to be at least 224x224 and then cropping from the center
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)

    # turn the image into a numpy array
    image_array = np.asarray(image)

    # Normalize the image
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1

    # Load the image into the array
    data[0] = normalized_image_array

    # Predicts the model
    prediction = model.predict(data)
    index = np.argmax(prediction)
    class_name = class_names[index]
    confidence_score = prediction[0][index]
    confidence_score2 = round(float(confidence_score), 3)
    return class_name, confidence_score2

@bot.message_handler(content_types=['photo'])
def save_picture(message):
    file_info = bot.get_file(message.photo[-1].file_id)
    file_name = file_info.file_path.split('/')[-1]
    full_name = "saved_photo/"+file_name
    downloaded_file = bot.download_file(file_info.file_path)
    with open(full_name, 'wb') as new_file:
        new_file.write(downloaded_file)

    no_name, confidence_score_3 = get_class(full_name)
    bot.send_message(message.chat.id, "Картинка загружена! Анализирую фото... ")
    if confidence_score_3 >= 0.6:
        bot.send_message(message.chat.id, "Это похоже на:")
        bot.reply_to(message, no_name)
    else:
        bot.send_message(message.chat.id, "Неуверен, что смогу узнать марку авто.")

@bot.message_handler(func = lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Это не картинка! Отправьте картинку, чтобы я смог ее загрузить!(или напишите /help)")


bot.polling()