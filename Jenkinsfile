#!groovy
@Library("ds-utils@v0.2.0") // Uses library from https://github.com/UIUCLibrary/Jenkins_utils
import org.ds.*

pipeline {
    agent any
    environment {
        mypy_args = "--junit-xml=mypy.xml"
        pytest_args = "--junitxml=reports/junit-{env:OS:UNKNOWN_OS}-{envname}.xml --junit-prefix={env:OS:UNKNOWN_OS}  --basetemp={envtmpdir}"
    }
    parameters {
        string(name: "PROJECT_NAME", defaultValue: "Hathi Submission Workflow", description: "Name given to the project")
        booleanParam(name: "UNIT_TESTS", defaultValue: true, description: "Run automated unit tests")
        booleanParam(name: "ADDITIONAL_TESTS", defaultValue: true, description: "Run additional tests")
        booleanParam(name: "PACKAGE", defaultValue: true, description: "Create a package")
        booleanParam(name: "DEPLOY_SCCM", defaultValue: false, description: "Create SCCM deployment package")
        booleanParam(name: "DEPLOY_DEVPI", defaultValue: true, description: "Deploy to devpi on http://devpy.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}")
        booleanParam(name: "UPDATE_DOCS", defaultValue: false, description: "Update online documentation")
        string(name: 'URL_SUBFOLDER', defaultValue: "hathi_submission_workflow", description: 'The directory that the docs should be saved under')
        string(name: 'JIRA_ISSUE', defaultValue: "", description: 'Jira task to generate about updates.')

    }
    stages {
        stage("Testing Jira issue"){
            agent any
            when {
                expression {params.JIRA_ISSUE != ""}
            }
            steps {
                echo "Finding Jira issue $params.JIRA_ISSUE"
                script {
                    // def result = jiraSearch "issue = $params.JIRA_ISSUE"
                    def result = jiraIssueSelector(issueSelector: [$class: 'JqlIssueSelector', jql: "issue = $params.JIRA_ISSUE"])
                    if(result){
                        echo "${result.getClass()}"
                    } else {
                        error("Jira issue $params.JIRA_ISSUE not found")
                    }
                }

            }
        }
        stage("Cloning and Generating Source") {
            agent {
                label "Windows"
            }

            steps {
                deleteDir()
                checkout scm
                virtualenv python_path: env.PYTHON3, requirements_file: "requirements.txt", windows: true, "python setup.py build"
                stash includes: '**', name: "Source", useDefaultExcludes: false

                stash includes: 'deployment.yml', name: "Deployment"
            }

        }

        stage("Unit tests") {
            when {
                expression { params.UNIT_TESTS == true }
            }
            steps {
                parallel(
                        "Windows": {
                            script {
                                def runner = new Tox(this)
                                runner.env = "pytest"
                                runner.windows = true
                                runner.stash = "Source"
                                runner.label = "Windows"
                                runner.post = {
                                    junit 'reports/junit-*.xml'
                                }
                                runner.run()
                            }
                        }
                        // "Windows": {
                        //     node(label: 'Windows') {
                        //         deleteDir()
                        //         unstash "Source"
                        //         bat "${env.TOX}  -e pytest"
                        //         junit 'reports/junit-*.xml'
                        //
                        //     }
                        // }
                        // "Linux": {
                        //     node(label: "!Windows") {
                        //         deleteDir()
                        //         unstash "Source"
                        //         withEnv(["PATH=${env.PYTHON3}/..:${env.PATH}"]) {
                        //             sh "${env.TOX}  -e pytest"
                        //         }
                        //         junit 'reports/junit-*.xml'
                        //     }
                        // }
                )
            }
        }
        stage("Additional tests") {
            when {
                expression { params.ADDITIONAL_TESTS == true }
            }

            steps {
                parallel(
                        "Documentation": {
                            script {
                                def runner = new Tox(this)
                                runner.env = "docs"
                                runner.windows = true
                                // runner.windows = false
                                runner.stash = "Source"
                                // runner.label = "!Windows"
                                runner.label = "Windows"
                                runner.post = {
                                    dir('.tox/dist/html/') {
                                        stash includes: '**', name: "HTML Documentation", useDefaultExcludes: false
                                    }
                                }
                                runner.run()

                            }
                        },
                        "MyPy": {
                            script {
                                def runner = new Tox(this)
                                runner.env = "mypy"
                                runner.windows = false
                                runner.stash = "Source"
                                runner.label = "!Windows"
                                runner.post = {
                                    junit 'mypy.xml'
                                }
                                runner.run()

                            }

                        }
                )
            }
        }

        stage("Packaging") {
            when {
                expression { params.PACKAGE == true }
            }

            steps {
                parallel(
                        "Windows Standalone": {
                            node(label: "Windows") {
                                deleteDir()
                                unstash "Source"
                                bat "call make.bat release"
//                                bat """${env.PYTHON3} -m venv .env
//                                        call .env/Scripts/activate.bat
//                                        pip install --upgrade pip setuptools
//                                        pip install -r requirements.txt
//                                        call make.bat release
//                                       IF NOT %ERRORLEVEL% == 0 (
//                                         echo ABORT: %ERRORLEVEL%
//                                         exit /b %ERRORLEVEL%
//                                       )
//                                    """


                                dir("dist") {
                                    archiveArtifacts artifacts: "*.msi*", fingerprint: true
                                    stash includes: "*.msi", name: "msi"
                                }
                            }
                        }, "Windows Wheel": {
                            node(label: "Windows") {
                                deleteDir()
                                unstash "Source"
                                bat "${env.PYTHON3} setup.py bdist_wheel --universal"
                                archiveArtifacts artifacts: "dist/**", fingerprint: true
                            }
                        },

                        "Source Release": {
                            createSourceRelease(env.PYTHON3, "Source")
                        }
                )
            }
        }

        stage("Deploy - Staging") {
            agent any
            when {
                expression { params.DEPLOY_SCCM == true && params.PACKAGE == true }
            }

            steps {
                deployStash("msi", "${env.SCCM_STAGING_FOLDER}/${params.PROJECT_NAME}/")
                input("Deploy to production?")
            }
        }

        stage("Deploy - SCCM upload") {
            agent any
            when {
                expression { params.DEPLOY_SCCM == true && params.PACKAGE == true }
            }

            steps {
                deployStash("msi", "${env.SCCM_UPLOAD_FOLDER}")
            }

            post {
                success {
                    script {
                        unstash "Source"
                        def deployment_request = requestDeploy this, "deployment.yml"
                        echo deployment_request
                        writeFile file: "deployment_request.txt", text: deployment_request
                        archiveArtifacts artifacts: "deployment_request.txt"
                    }
                }
            }
        }
        stage("Deploying to Devpi") {
            agent {
                node {
                    label 'Windows'
                }
            }
            when {
                expression { params.DEPLOY_DEVPI == true }
            }
            steps {
                deleteDir()
                unstash "Source"
                bat "devpi use http://devpy.library.illinois.edu"
                withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                    bat "devpi login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                    bat "devpi use /${DEVPI_USERNAME}/${env.BRANCH_NAME}"
                    script {
                        try{
                            bat "devpi upload --with-docs"

                        } catch (exc) {
                            echo "Unable to upload to devpi with docs. Trying without"
                            bat "devpi upload"
                        }
                    }
                    bat "devpi test hsw"
                }

            }
        }
        stage("Update online documentation") {
            agent any
            when {
                expression { params.UPDATE_DOCS == true }
            }

            steps {
                deleteDir()
                script {
                    updateOnlineDocs url_subdomain: params.URL_SUBFOLDER, stash_name: "HTML Documentation"

                }
            }
        }
    }
}
