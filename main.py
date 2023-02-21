import sys
import requests
import pygame
import os


pygame.init()
apikey = "40d1649f-0493-4b70-98ba-98533de7710b"
spn1, spn2 = "0.01", "0.01"
coords1, coords2 = map(str, "55.752027, 37.613576".split(", "))
l = "map"
pt = None
adrs = ""


def geocode(address):
    req = f"http://geocode-maps.yandex.ru/1.x/?apikey={apikey}&geocode={address}&format=json"
    res = requests.get(req)
    if res:
        json_res = res.json()
    else:
        raise RuntimeError(
            """Ошибка выполнения запроса:
            {request}
            Http статус: {status} ({reason})""".format(
                request=req, status=res.status_code, reason=res.reason))
    features = json_res["response"]["GeoObjectCollection"]["featureMember"]
    if features:
        global spn1, spn2, coords1, coords2, pt, img, adrs
        coords2, coords1 = features[0]["GeoObject"]["Point"]["pos"].split(" ")
        pt = "{0},{1}".format(coords2, coords1)
        spn1, spn2 = "0.01", "0.01"
        adrs = features[0]["GeoObject"]["metaDataProperty"]["GeocoderMetaData"]["text"]
        img = search()


def change_spn(flag):
    global spn1, spn2
    if flag:
        preres = float(spn1) * 2, float(spn2) * 2
    else:
        preres = float(spn1) / 2, float(spn2) / 2
    if 0.0001 < preres[0] < 0.1 and 0.0001 < preres[1] < 0.05:
        spn1, spn2 = [str(i) for i in preres]


def move(direct):
    global coords1, coords2
    if direct == "up":
        coords1 = str(float(coords1) + float(spn2))
    elif direct == "down":
        coords1 = str(float(coords1) - float(spn2))
    elif direct == "left":
        coords2 = str(float(coords2) - float(spn1))
    else:
        coords2 = str(float(coords2) + float(spn1))


def search():
    maps_server = 'http://static-maps.yandex.ru/1.x/'
    map_params = {
        'll': coords2 + ',' + coords1,
        'spn': spn1 + ',' + spn2,
        'l': l
    }
    if pt:
        map_params['pt'] = "{0},pm2dgl".format(pt)
    response = requests.get(maps_server, params=map_params)
    with open('map.png', 'wb') as f:
        f.write(response.content)
    image = pygame.image.load('map.png')
    os.remove('map.png')
    return image


def terminate():
    pygame.quit()
    sys.exit()


font = pygame.font.Font(None, 32)
font1 = pygame.font.Font(None, 20)
pygame.display.set_caption('YL-MAP')
img = search()
size = width, height = img.get_width() + 100, img.get_height() + 150
screen = pygame.display.set_mode(size)
running = True
img = search()

input_box = pygame.Rect(10, img.get_height() + 10, 400, 32)
color_inactive = pygame.Color('lightskyblue3')
color_active = pygame.Color('dodgerblue2')
color = color_inactive
active = False
text = ''
done = False

reset_btn = pygame.Rect(10, img.get_height() + 110, 335, 30)

FPS = 50
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        if event.type == pygame.KEYDOWN:
            if active:
                if event.key == pygame.K_RETURN:
                    geocode(text)
                    text = ''
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode
            else:
                if event.key == pygame.K_PAGEDOWN:
                    change_spn(True)
                elif event.key == pygame.K_PAGEUP:
                    change_spn(False)
                elif event.key == pygame.K_UP:
                    move("up")
                elif event.key == pygame.K_DOWN:
                    move("down")
                elif event.key == pygame.K_LEFT:
                    move("left")
                elif event.key == pygame.K_RIGHT:
                    move("right")
                elif event.key == pygame.K_F1:
                    l = "map"
                elif event.key == pygame.K_F2:
                    l = "sat"
                elif event.key == pygame.K_F3:
                    l = "sat,skl"
                img = search()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if input_box.collidepoint(event.pos):
                active = not active
            else:
                active = False
            color = color_active if active else color_inactive
            if reset_btn.collidepoint(event.pos):
                pt = None
                adrs = ""
                img = search()
    screen.fill((0, 0, 0))
    screen.blit(img, (50, 0))
    txt_surface = font.render(text, True, color)
    width = max(400, txt_surface.get_width() + 10)
    input_box.w = width
    screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
    pygame.draw.rect(screen, color, input_box, 2)
    txt_surface = font.render('Сброс поискового результата', True, color_active)
    screen.blit(txt_surface, (reset_btn.x + 5, reset_btn.y + 5))
    pygame.draw.rect(screen, color_active, reset_btn, 2)
    txt_surface = font1.render(("Адрес: " if adrs else "") + adrs, True, color_active)
    screen.blit(txt_surface, (input_box.x + 5, input_box.y + 52))
    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()