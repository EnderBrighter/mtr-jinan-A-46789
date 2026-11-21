# v17：LCD 与顶棚接缝

修复升高后的 LCD 外壳与原高度顶棚侧衬之间的高度/截面断差。每处 LCD 两端各增加 175 mm 长的渐变过渡，外壳和两端过渡改为一个闭合模型；过渡端与相邻顶棚使用同一个 COVE_PROFILE，消除两种轮廓在边缘错开的透天三角缺口。三种车体、两侧共30处同步修正。

屏幕宽高、倾角、坐标与动态脚本不变；偏灰内饰、外观纹理和门体几何均保持v16。门位与开门行程不变。

验证：交付OBJ的360条接缝射线均命中朝向车内的不透明过渡面；150条屏面视线无遮挡；全部30处外壳和过渡闭合；门叶完整连续扫掠无碰撞；五线纹理、LCD脚本和门立方体形状与v16一致；两个ZIP CRC与运行文件一致性通过。

交付：dist/jinan_lines_4_6_7_8_9_v17.zip（五线合辑）、dist/jinan_line4_no_logo_v17.zip（4号线独立版）。旧ZIP保留。请只启用其中一个版本。

preview/v17_lcd_join_right.png、v17_lcd_join_left.png、v17_lcd_interior.png 为Blender渲染预览，非游戏截图；尚未游戏内重载确认。工程source/jinan_line4_v17.blend。修改前备份source/archive/before_v17_lcd_join.zip。

重建：python source/generate_pack.py，然后python source/build_multiline.py。接缝检查：python source/check_v17.py。
