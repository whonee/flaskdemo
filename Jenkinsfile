pipeline {
    // 1. 指定在测试节点运行
    agent { 
        label 'ubuntu-node-1' 
    }

    environment {
        // 项目配置
        IMAGE_REPO = "crpi-kkwnyjxyawe2f42w.cn-hangzhou.personal.cr.aliyuncs.com/ygg12138ali/whonee.flask" // 替换为你的镜像仓库地址
        IMAGE_TAG = "${env.BUILD_NUMBER}"
        CONTAINER_NAME = "flask-prod"
        PROD_PORT = "8000"
        
        // 阿里云服务器信息
        ALIYUN_USER = "jenkins"
        ALIYUN_HOST = "aliyun" // 替换为阿里云公网IP

        // 手动触发时，env.BRANCH_NAME 通常是 null
        // 需要手动设置或使用默认值
        BRANCH_NAME = "${env.BRANCH_NAME ?: 'main'}"
    }

    stages {
        // 阶段一：拉取代码
        stage('Checkout') {
            steps {
                echo '正在拉取代码...'
                git branch: 'main', url: 'git@github.com:whonee/flaskdemo.git',
                credentialsId: 'github-key'
            }
        }

        // 阶段二：单元测试 (在 Node1 上跑)
        stage('Unit Test') {
            steps {
                echo '正在运行单元测试...'
                // 使用 venv 隔离环境，防止污染 Node1
                sh '''
                    uv sync
                    # 运行测试 (假设你有测试文件)
                    uv pip install -e .
                    uv run coverage run -m pytest
                    uv run coverage html
                '''
            }
        }

        // 阶段三：构建镜像并推送
        stage('Build & Push Docker Image') {
            steps {
                script {
                    echo '构建 Docker 镜像...'
                    // 登录镜像仓库
                    withCredentials([usernamePassword(credentialsId: 'ali-image-repo', passwordVariable: 'DOCKER_PWD', usernameVariable: 'DOCKER_USER')]) {
                        sh '''
                        echo "$DOCKER_PWD" | docker login --username="$DOCKER_USER" crpi-kkwnyjxyawe2f42w.cn-hangzhou.personal.cr.aliyuncs.com --password-stdin
                        '''
                    }
                    
                    // 构建镜像
                    sh "docker build -t ${IMAGE_REPO}:${IMAGE_TAG} ."
                    sh "docker tag ${IMAGE_REPO}:${IMAGE_TAG} ${IMAGE_REPO}:latest"
                    
                    // 推送镜像
                    sh "docker push ${IMAGE_REPO}:${IMAGE_TAG}"
                    sh "docker push ${IMAGE_REPO}:latest"
                    
                    // 清理本地临时镜像
                    sh "docker rmi ${IMAGE_REPO}:${IMAGE_TAG} || true"
                }
            }
        }

        // 阶段四：部署到测试环境 (Node1 本机验证) - 可选
        stage('Deploy to Test') {
            steps {
                sh """
                    docker rm -f flask-test || true
                    docker run -d --name flask-test -p 5000:5000 -v ~/flaskdemo/instance/:/app/instance/ ${IMAGE_REPO}:latest
                """
                // 简单的健康检查
                sh "sleep 10 && curl -f http://localhost:5000/hello || exit 1"
                sh "docker rm -f flask-test || true"
            }
        }

        // 阶段五：部署到生产环境 (Aliyun)
        stage('Deploy to Prod (Aliyun)') {
            // 仅在 main 分支变更时才部署生产环境
            when {
                branch 'main'
            }
            steps {
                echo '正在部署到阿里云...'
                // 使用 ssh-agent 注入私钥，远程执行 Docker 命令
                withCredentials([sshUserPrivateKey(credentialsId: 'aliyun-jenkins-agent', keyFileVariable: 'SSH_KEY_FILE')]){
                    sh """
                            ssh -o StrictHostKeyChecking=no -i "${SSH_KEY_FILE}" "${ALIYUN_USER}@${ALIYUN_HOST}" '
                            # 1. 登录仓库 (如果仓库是私有的)
                            # docker login registry.cn-hangzhou.aliyuncs.com -u [用户名] -p [密码] 
                            
                            # 2. 拉取最新镜像
                            docker pull ${IMAGE_REPO}:${IMAGE_TAG}
                            
                            # 3. 停止并删除旧容器
                            docker rm -f ${CONTAINER_NAME} || true
                            
                            # 4. 启动新容器 (建议用 Gunicorn 启动 Flask)
                            docker run -d \\
                                --name ${CONTAINER_NAME} \\
                                --restart always \\
                                -p ${PROD_PORT}:5000 \\
                                -v ~/flaskdemo/instance/:/app/instance/ \\
                                ${IMAGE_REPO}:${IMAGE_TAG}
                        '
                    """
                }
            }
        }
    }
    
    post {
        always {
            emailext(
                subject: "【${currentBuild.currentResult}】${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: """
                <h3>构建报告</h3>
                <p><b>项目：</b>${env.JOB_NAME}</p>
                <p><b>状态：</b>${currentBuild.currentResult}</p>
                <p><b>编号：</b>#${env.BUILD_NUMBER}</p>
                <p><b>时长：</b>${currentBuild.durationString}</p>
                <p><b>详情：</b><a href="${env.BUILD_URL}">${env.BUILD_URL}</a></p>
                """,
                to: 'whonee1@163.com',
                mimeType: 'text/html'
            )
        }
    }
}