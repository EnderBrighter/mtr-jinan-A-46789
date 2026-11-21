# 济南地铁追加包 v11

这是GPT-6.1-sol (High)接入Codex制作。

版本：MTR 4.0.5，JCM 2.3.0。新生成的ZIP不附带 `使用说明.md`。

适用：Minecraft 1.20.4 Fabric / MTR 4.0.5 / JCM 2.3.0。

当前工作文件夹是 4/6/7/8/9 号线合辑，共20个车辆定义（每线 Tc / M / Mp / 反向Tc），沿用原车体尺寸和动态LCD功能。4号线车辆ID保留，原有存档继续兼容。新增线路是按要求制作的同模型配色版本，不代表各线实际车辆结构。

- `dist/jinan_line4_no_logo_v11.zip`：4号线无标志独立版。
- `dist/jinan_lines_4_6_7_8_9_v11.zip`：五线合辑。
- 文件夹、独立版ZIP、合辑ZIP三者选择一个启用，不要重复叠加。ZIP需复制到resourcepacks根目录才能在游戏资源包列表选取；dist子目录不会单独被扫描。
- 车头仿logo已去除，保留白色圆角矩形；所有车号分别为0401、0601、0701、0801、0901。
- 外观及普通座椅变色，原黄色端部座位的坐垫、靠背保持原色。
- 4号线撤回草木绿调整，恢复上一稿：外观 #B1D93E、普通座椅 #9DD91D；最终按用户“美观优先、不能刺眼”要求降低饱和度：外观6号线 #55B7D5、7号线 #C65054、8号线 #8965AE、9号线 #B69452；普通座椅分别为 #74BDCF、#CB7474、#9A83B6、#BBA071。黄色座位仍为原色 #EFC944。9号线以参考图 #BC9037 为基调柔化，不采用 #888600。

## 颜色参考

查询色表：https://wiki.southaki.top/zh-hans/济南轨道交通

列车主题色说明：https://jinan.dzwww.com/jrtt/202510/t20251022_16624751.htm

用户提供JPEG主体区域提取：4号线 #188F3B、6号线 #2ABAEE、7号线 #EF1917、8号线 #5E3790、9号线 #BC9037。查询色仅作为色系参考，最终采用柔和的列车涂装配色；4号线按用户最新要求恢复上一稿黄绿色；9号线以用户图片金土黄为基调。JPEG采样不等于官方印刷色规范。

## 启动/减速无声排查（按用户要求暂缓）

已核对本机正式版MTR 4.0.5 JAR：原配置与内置SP1900一致，legacySpeedSoundBaseResource=sp1900、legacySpeedSoundCount=120。加速/减速共240个事件全部存在，对应OGG可解码且全部非静音；日志没有发现SP1900缺失事件，Minecraft各相关音量也不是0。没有发现本资源包缺音频或拼错路径的证据。保留原生SP1900音效，不引入无依据的替代音效。

尚未完成游戏内动态复现，因此不能据此断言是Mod bug，也不声称无声问题已经修好。静态审计记录见工作目录inspection/v11_audio_audit.json。

可在允许命令的世界里依次试听：

```
/playsound mtr:sp1900_acceleration_5a master @s ~ ~ ~ 1 1
/playsound mtr:sp1900_deceleration_5a master @s ~ ~ ~ 1 1
```

若命令能出声、运行中的内置SP1900也无声，优先排查MTR/渲染裁剪与其他Mod的交互；若内置车正常，仅本包车辆无声，需要对同一线路、同一视角和乘坐状态进行对照。MTR旧声音播放依赖车辆渲染回调、非暂停状态和200ms调度，静态资源检查无法验证游戏运行时是否触发。

## 重建与备份

先运行 `python source/generate_pack.py` 更新4号线源模型，再运行 `python source/build_multiline.py` 派生合辑和两个ZIP。动态LCD仍从实际游戏线路读取站名和线路色，不写死现实站表。

修改前运行资源、生成源码与Blender工程备份：source/archive/before_multiline_v11.zip。旧版dist文件保留。
