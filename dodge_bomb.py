import os
import sys
import pygame as pg
import random
import time
import math


WIDTH, HEIGHT = 1100, 650
DELTA = {pg.K_UP:(0, -5), pg.K_DOWN:(0, +5), pg.K_LEFT:(-5, 0), pg.K_RIGHT:(+5, 0)} # 練習1
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数で指定されたrctが画面内か画面外か判定する関数
    引数:こうかとんRectかばくだんRect
    戻り値:タプル(横方向判定結果,縦方向判定結果)
    """
    yoko, tate = True, True
    if rct.left < 0 or WIDTH < rct.right:  # 横方向判定
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom:  # 縦方向判定
        tate = False
    return yoko, tate


def gameover(screen: pg.Surface) -> None:
    """
    ゲームオーバー画面を表示する関数
    引数:screen
    """
    black_image = pg.Surface((1100, 650))  # 黒surface
    pg.draw.rect(black_image, (0,0,0), (0, 0, 1100, 650))
    black_image.set_alpha(200)  # 透明度
    fonto = pg.font.Font(None, 80)
    go_txt = fonto.render("Game Over", True, (255, 255, 255))
    black_image.blit(go_txt, [400, 300])
    kk_go_img = pg.image.load("fig/8.png")
    black_image.blit(kk_go_img, [330, 290])  # Game Over 表示
    black_image.blit(kk_go_img, [730, 290])  # こうかとん表示
    screen.blit(black_image, [0, 0])
    pg.display.update()  # 画面再読み込み
    time.sleep(5)  # 5秒ストップ

    return


def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    爆弾Surfaceと加速度のリストをまとめたタプルを返す関数
    戻り値:2つのリストをまとめたタプル
    """
    bb_imgs = []
    for r in range(1, 11):
        bb_img = pg.Surface((20*r, 20*r))
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        bb_imgs.append(bb_img)
    bb_accs=[a for a in range(1, 11)]

    return (bb_imgs, bb_accs)


#3.飛ぶ方向に従ってこうかとん画像を切り替える
def get_kk_imgs(kk_img: pg.Surface) -> dict[tuple[int, int], pg.Surface]:
    img0 = kk_img # 左向き
    img1 = pg.transform.flip(img0, True, False) #左右反転

    kk_dict = {
        ( 0,  0): pg.transform.rotozoom(img1,   0, 1.0), # 初期
        (+5,  0): pg.transform.rotozoom(img1,   0, 1.0), # 右
        (+5, -5): pg.transform.rotozoom(img1,  45, 1.0), # 右上
        ( 0, -5): pg.transform.rotozoom(img1,  90, 1.0), # 上
        (-5, -5): pg.transform.rotozoom(img0, -45, 1.0), # 左上
        (-5,  0): pg.transform.rotozoom(img0,   0, 1.0), # 左
        (-5, +5): pg.transform.rotozoom(img0,  45, 1.0), # 左下
        ( 0, +5): pg.transform.rotozoom(img1, -90, 1.0), # 下
        (+5, +5): pg.transform.rotozoom(img1, -45, 1.0), # 右下
    }
    return kk_dict


def calc_orientation(org: pg.Rect, dst: pg.Rect, current_xy: tuple[float, float]) -> tuple[float, float]:
    """
    爆弾からこうかとんへの方向ベクトルを返す関数
    引数: org: 爆弾Rect
         dst: こうかとんRect
         current_xy: 現在の速度ベクトル
    戻り値：正規化された方向ベクトル
    """
    dx = dst.centerx - org.centerx
    dy = dst.centery - org.centery

    dist = math.sqrt(dx**2 + dy**2)

    # 近すぎるときはそのまま
    if dist < 300:
        return current_xy

    # 正規化（長さ√50 ≒ 7.07）
    if dist != 0:
        dx = dx / dist * 7
        dy = dy / dist * 7

    return dx, dy


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    kk_img0 = pg.image.load("fig/3.png")  # 読み込み
    kk_imgs = get_kk_imgs(kk_img0)  # 初期画像

    bb_img = pg.Surface((20, 20))  # 爆弾用の空のSurfaceを作る
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10)  # 爆弾円を描く
    bb_img.set_colorkey((0, 0, 0))  # 爆弾の黒い部分を透過させる
    bb_rct = bb_img.get_rect()  # 爆弾Rectを取得する
    bb_rct.centerx = random.randint(0, WIDTH)  # 爆弾の初期横座標を設定する
    bb_rct.centery = random.randint(0, HEIGHT)  # 爆弾の初期縦座標を設定する
    vx, vy = +5, +5  # 爆弾の速度

    bb_imgs, bb_accs = init_bb_imgs()  # 爆弾surface,加速度のリスト

    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
            
        if kk_rct.colliderect(bb_rct):  # こうかとんと爆弾の衝突判定
            gameover(screen)
            return  # ゲームオーバーの意
        
        screen.blit(bg_img, [0, 0]) 

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]

        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]

        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):  # 画面外だったら
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])
        
        kk_img = kk_imgs[tuple(sum_mv)]  # こうかとん画像辞書から取り出し
        screen.blit(kk_img, kk_rct)

        bb_rct.move_ip(vx, vy)  # 爆弾を移動させる
        yoko, tate = check_bound(bb_rct)
        if not yoko:  # 横方向判定
            vx *= -1
        if not tate:  # 縦方向判定
            vy *= -1
        screen.blit(bb_img, bb_rct)  # 爆弾を表示させる

        avx = vx*bb_accs[min(tmr//500, 9)]
        avy = vy*bb_accs[min(tmr//500, 9)]
        bb_img = bb_imgs[min(tmr//500, 9)]
        bb_img.set_colorkey((0, 0, 0))  # 黒部分の透明化

        bb_rct.move_ip(avx, avy)  # 加速

        vx, vy = calc_orientation(bb_rct, kk_rct, (vx, vy))
        bb_rct.move_ip(vx, vy)
        
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
