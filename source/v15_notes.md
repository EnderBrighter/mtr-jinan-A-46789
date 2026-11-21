# v15：降低内饰亮度、统一门板与墙板、修正白色内衬渲染层

适用 Minecraft 1.20.4 Fabric / MTR 4.0.5 / JCM 2.3.0。同步4/6/7/8/9号线。

v14 的白色固定内衬使用 ALWAYS_ON_LIGHT。已核对本机 MTR 4.0.5 RenderStage：该阶段对应 TRANSLUCENT_GLOWING，属于透明渲染。这个设置与不透明车体内衬不符，存在遮挡排序风险。本版将全部固定白色内衬换成 LIGHT（CUTOUT_GLOWING，不透明裁切）。从内部核对车头下部、上部和两侧内衬，28条射线命中朝内实体面；保留驾驶室及侧窗原本的清透玻璃。

门内侧白板从门的其余部件中分组，使用与墙板、顶棚、椅壳、LCD外壳完全相同的 LIGHT 不透明阶段、同一 atlas 白色色块 #D8DCD7。颜色从 v14 的 #E7EBE7 降低，维持柔和的浅灰白。原生门白色面 shade=false，与固定白板无方向压暗的受光方式相配。银色外壳、地板、扶手、座椅主题色均沿用v14。

本次只改变白板颜色及渲染分组；门坐标、尺寸、inflate、UV、开门行程没有变化。LCD 保留恢复后的 1.74 m宽、0.285 m竖直高度与上移安装；黄色座位位置和v13默认线路标识色逻辑保留。

检查通过：五线门体逐立方体几何对比；门板和固定白板阶段一致、alpha均为255；OBJ全部分组都有配置；车头内衬朝向及覆盖；35条外壳射线、模型表面三角化、五块驾驶室玻璃；完整门叶连续扫掠、正反向101开度；150条LCD可见性射线和30处封闭外壳；两个新ZIP CRC与资源内容一致。

preview/v15_cab_inside.png、v15_door_panels.png、v15_interior.png 为Blender渲染预览，不是游戏截图。尚未游戏内重载验证，不能据此确认用户环境下的透明问题已经完全消失。

交付：dist/jinan_lines_4_6_7_8_9_v15.zip（五线合辑），dist/jinan_line4_no_logo_v15.zip（4号线独立版）。旧ZIP保留，加载时只启用一个版本。

工程：source/jinan_line4_v15.blend。备份：source/archive/before_v15_unified_panels.zip。重建：python source/generate_pack.py，python source/build_multiline.py。
