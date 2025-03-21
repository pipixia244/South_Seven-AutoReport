# South Seven Technical School(SSTS)健康打卡平台自动打卡脚本 可用github action

# 恭喜SSTS将于2月25日20点起取消健康打卡，跨校区与出校申请报备模块！好似喵好似喵

# 恭喜SSTS在历经9个月的重重审批制后重回报备制！
# 根据最新通知，健康打卡平台不再需要上传健康码、核酸报告、大数据行程卡，原代码将归档为`report.py.old`，新代码为简化版本。

## 说明

**本打卡脚本仅供学习交流使用，请勿过分依赖。 开发者对使用或不使用本脚本造成的问题不负任何责任，不对脚本执行效果做出任何担保，原则上不提供任何形式的技术支持。**

## 更新记录
- 新增：
  - 20221208：取消与两码一核酸上传/审批有关的代码，只保留健康打卡与跨校区报备功能，原代码归档；简化命令行参数，支持选择目前居住地在校内/校外市内。Github Action配置跟随命令行参数的改动而进行微调。**恭喜SSTS在历经9个月的重重审批制后重回报备制！**
  - 20220605：实验性功能，如因配置此功能而出现任何问题，本脚本依旧不负任何责任，仅供交流学习使用。在校学生可以添加在secret内添加`PHONE`，值为自己的手机号。将调用官方接口获取大数据行程卡。如地址不在学校，请不要使用此功能！否则后果自负。
  - 20220527：修复bug。目前如果用户提供了图片url，则会强制替换原先存在于网站中的图片并取消最后的删除动作，而不是和空码的动作相同。
  - 重要消息：近几天得知，上传空码有可能会被上报（标记失信），因此恢复了原先去掉的删除功能。目前报备的整体逻辑为：先打卡，打卡后看有没有上传两码，如果有上传则跳过直接进行出校报备，如果没有上传则上传“空码”并出校报备，并在报备成功后删除之前上传的空码。如果用户指定了url，行为见20220527的记录。这样可以避免被上报的问题。
  - 20220509：适配新的图片上传api，以及新的报备url。
  - 20220424：增加上传两码功能，在每天报备前会先上传两码，以免报备失败。两码图片需使用直链链接，并存储在secrets中，取名`BIGDATA_URL` `ANKANG_URL`。当未设置这两个secrets或者secrets值为空时，脚本会使用仓库内的默认两码图片，该两码图片不含任何信息，只作为占位使用；更改报备时间，将报备时间集中在晚上和凌晨，以免影响白天班主任的两码一核酸的审核工作。
  - 20220321: 适配新的封校报备格式.
  - 20220319：适配新的健康打卡数据, <健康打卡>默认居住地为中校区. <封校报备>默认跨校区目的地为所有校区.
  - 20220318：更改<出校报备>功能, 适配新的<封校报备>功能.
  - 20210917：增加自动检测并报备<出校报备>功能.
  - 20210821：使用pytesseract识别登录二维码，支持二维码验证登录打卡。
  - 20210818：适配新的打卡数据, 将新增的敏感信息以参数方式传递, 放入secrets中。

- 原fork：
  - 20200831：增强稳定性
  - 20200827：增加打卡失败重试功能，增加License
  - 20200826：为配合学校最新规定，切换至Github Actions实现一天三次打卡
 
## 使用方法

-2. **请自行修改report.yml，以适配自身需求。fork后原始的report.yml有两条python命令可以给两人打卡，如不需要请删除第二个以免一直报错。**

-1. **数据有两个，一个是在家data_athome.json(需要自行修改地址)，另一个是在学校data_atschool.json(默认参数住中区)。请在report.yml中自行修改设置。**

0. **写在前面：请在自己fork的仓库中修改，并push到自己的仓库，不要直接修改本仓库，也不要将您的修改pull request到本仓库（对本仓库的改进除外）！如果尚不了解github的基本使用方法，请参阅[使用议题和拉取请求进行协作/使用复刻](https://docs.github.com/cn/github/collaborating-with-issues-and-pull-requests/working-with-forks)和[使用议题和拉取请求进行协作/通过拉取请求提议工作更改](https://docs.github.com/cn/github/collaborating-with-issues-and-pull-requests/proposing-changes-to-your-work-with-pull-requests)。**

1. 将本代码仓库fork到自己的github。

2. 根据自己的实际情况修改`data.json`的数据，参看下文。**开发者不保证这些模板的正确性。**

3. 将修改好的代码push至master分支。如果不需要修改 `data.json`，请在 `README.md` 里添加一个空格并push，否则不会触发之后的步骤。**请在自己的仓库中修改，不要pull request到本仓库！**

4. 点击Actions选项卡，点击`I understand my workflows, go ahead and enable them`.

5. 为保护隐私，需要将私人信息放入secrets中传递参数。点击Settings选项卡，点击左侧Secrets，点击New secret，创建名为`STUID`，值为自己学号的secret。用同样方法，创建名为`PASSWORD`，值为自己中国滑稽大学统一身份认证密码的secret。并接着创建`EMER_PERSON` `EMER_RELA` `EMER_PHONE`三个secret，分别代表打卡界面的紧急联系人，与ta的关系，紧急联系人电话。这几个值不会被公开。

   ![secrets](imgs/image-20200826215037042.png)

6. 默认每6小时打卡一次。如需选择其它时间，可以修改`.github/workflows/report.yml`中的`cron`，详细说明参见[安排的事件](https://docs.github.com/cn/actions/reference/events-that-trigger-workflows#scheduled-events)，请注意这里使用的是**国际标准时间UTC**，北京时间的数值比它大8个小时。建议修改默认时间，避开打卡高峰期以提高成功率。

7. 在Actions选项卡可以确认打卡情况。如果打卡失败（可能是临时网络问题等原因），脚本会自动重试，五次尝试后如果依然失败，将返回非零值提示构建失败。

8. 在Github个人设置页面的Notifications下可以设置Github Actions的通知，建议打开Email通知，并勾选"Send notifications for failed workflows only"。

## 在本地运行测试

要在本地运行测试，需要安装python 3。我们假设您已经安装了python 3和pip 3，并已将其路径添加到环境变量。

### 安装依赖

```shell
apt install tesserart
pip install -r requirements.txt
pip install pillow pytesserart
```

### 运行打卡程序

```shell
python report.py [DATA] [STUID] [PASSWORD] [EMER_PERSON] [EMER_RELA] [EMER_PHONE]
```
其中，`[DATA]`是存放打卡数据的json文件的路径，`[STUID]`是学号，`[PASSWORD]`是统一身份认证的密码明文。EMER_PERSON EMER_RELA EMER_PHONE，分别代表打卡界面的紧急联系人，与ta的关系，紧急联系人电话。

## data.json 数据获取方法

使用 F12 开发者工具抓包之后得到数据，按照 json 格式写入 `data.json` 中。

1. 登录进入打卡系统，打开开发者工具（Chrome 可以使用 F12 快捷键），选中 Network 窗口：

![](./imgs/1.png)

2. 点击确认上报，点击抓到的 `daliy_report` 请求，在 `Headers` 下面找到 `Form Data` 这就是每次上报提交的信息参数。

![](./imgs/2.png)

3. 将找到的 Data 除 `_token` （每次都会改变，所以不需要复制，脚本中会每次获取新的 token 并添加到要提交的数据中）外都复制下来，存放在 `data.json` 中，并参考示例文件转换为对应的格式。

4. 通过push操作触发构建任务，检查上报数据是否正确。

## 许可

MIT License

Copyright (c) 2020 BwZhang

Copyright (c) 2020 Violin Wang

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

