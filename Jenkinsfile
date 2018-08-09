#!groovy
@Library("ds-utils@v0.2.0") // Uses library from https://github.com/UIUCLibrary/Jenkins_utils
import org.ds.*

def PKG_NAME = "unknown"
def PKG_VERSION = "unknown"
def DOC_ZIP_FILENAME = "doc.zip"
def junit_filename = "junit.xml"
def REPORT_DIR = ""
def VENV_ROOT = ""
def VENV_PYTHON = ""
def VENV_PIP = ""

pipeline {
    agent {
        label "Windows && Python3"
    }
    options {
        disableConcurrentBuilds()  //each branch has 1 job running at a time
        timeout(60)  // Timeout after 60 minutes. This shouldn't take this long but it hangs for some reason
        checkoutToSubdirectory("source")
    }
    triggers {
        cron('@daily')
    }
    environment {
        mypy_args = "--junit-xml=mypy.xml"
        pytest_args = "--junitxml=reports/junit-{env:OS:UNKNOWN_OS}-{envname}.xml --junit-prefix={env:OS:UNKNOWN_OS}  --basetemp={envtmpdir}"
    }

    parameters {
        booleanParam(name: "FRESH_WORKSPACE", defaultValue: false, description: "Purge workspace before staring and checking out source")
        booleanParam(name: "UNIT_TESTS", defaultValue: true, description: "Run Automated Unit Tests")
        booleanParam(name: "ADDITIONAL_TESTS", defaultValue: true, description: "Run additional tests")
        booleanParam(name: "DEPLOY_DEVPI", defaultValue: true, description: "Deploy to devpi on http://devpy.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}")
        choice(choices: 'None\nRelease_to_devpi_only\nRelease_to_devpi_and_sccm\n', description: "Release the build to production. Only available in the Master branch", name: 'RELEASE')
        booleanParam(name: "UPDATE_DOCS", defaultValue: false, description: "Update the documentation")
        string(name: 'URL_SUBFOLDER', defaultValue: "DCCMedusaPackager", description: 'The directory that the docs should be saved under')
        // booleanParam(name: "PACKAGE", defaultValue: true, description: "Create a Packages")
        // booleanParam(name: "DEPLOY", defaultValue: false, description: "Deploy SCCM")
//    //////////////////

        string(name: "PROJECT_NAME", defaultValue: "Hathi Submission Workflow", description: "Name given to the project")
        booleanParam(name: "UNIT_TESTS", defaultValue: true, description: "Run automated unit tests")
        booleanParam(name: "ADDITIONAL_TESTS", defaultValue: true, description: "Run additional tests")
        booleanParam(name: "PACKAGE", defaultValue: true, description: "Create a package")
        // booleanParam(name: "DEPLOY_SCCM", defaultValue: false, description: "Create SCCM deployment package")
        choice(choices: 'None\nRelease_to_devpi_only\nRelease_to_devpi_and_sccm\n', description: "Release the build to production. Only available in the Master branch", name: 'RELEASE')
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
                    if(result.isEmpty()){
                        echo "Jira issue $params.JIRA_ISSUE not found"
                        error("Jira issue $params.JIRA_ISSUE not found")

                    } else {
                        echo "Located ${result}"
                    }
                }

            }
        }
        stage("Cloning and Generating Source") {
            steps {
                deleteDir()
                checkout scm
                // virtualenv python_path: "${tool 'Python3.6.3_Win64'}", requirements_file: "requirements.txt", windows: true, "python setup.py build"
                bat """${tool 'Python3.6.3_Win64'} -m venv venv
                    call venv\\Scripts\\activate.bat
                    pip install -r requirements.txt
                    pip install -r requirements-dev.txt
                    python setup.py build
"""
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
                                // runner.label = "Linux"
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
                                runner.label = "Linux"
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
                            node(label: "Windows&&VS2015&&DevPi") {
                                deleteDir()
                                unstash "Source"
                                bat "call make.bat release"
//                                bat """${tool 'Python3.6.3_Win64'} -m venv .env
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
                        }, 
                        "Source and Wheel formats": {
                            bat """${tool 'Python3.6.3_Win64'} -m venv venv
                                    call venv\\Scripts\\activate.bat
                                    pip install -r requirements.txt
                                    pip install -r requirements-dev.txt
                                    python setup.py sdist bdist_wheel
                                    """
                        }
//                         "Windows Wheel": {
//                             node(label: "Windows") {
//                                 deleteDir()
//                                 unstash "Source"
//                                 bat "${tool 'Python3.6.3_Win64'} setup.py bdist_wheel"
//                                 archiveArtifacts artifacts: "dist/**", fingerprint: true
//                             }
//                         },

//                         "Source Release": {
//                             node(label: "Windows") {
//                                 deleteDir()
//                                 unstash "Source"
//                                 bat "${tool 'Python3.6.3_Win64'} setup.py sdist"
//                                 archiveArtifacts artifacts: "dist/**", fingerprint: true
//                             }
// //                            node(label: Linux) {
// //                                createSourceRelease(env.PYTHON3, "Source")
// //                            }

//                         }
                )
            }
            post {
              success {
                  dir("dist"){
                      unstash "msi"
                      archiveArtifacts artifacts: "*.whl", fingerprint: true
                      archiveArtifacts artifacts: "*.tar.gz", fingerprint: true
                      archiveArtifacts artifacts: "*.msi", fingerprint: true
                }
              }
            }
        }

        // stage("Deploy to SCCM") {
        //     when {
        //         expression { params.RELEASE == "Release_to_devpi_and_sccm"}
        //     }

        //     // agent any
        //     // when {
        //     //     expression { params.DEPLOY_SCCM == true && params.PACKAGE == true }
        //     // }

        //     steps {
        //         deployStash("msi", "${env.SCCM_STAGING_FOLDER}/${params.PROJECT_NAME}/")
        //         input("Deploy to production?")
        //     }
        // }
        stage("Deploying to Devpi staging") {
            when {
                expression { params.DEPLOY_DEVPI == true }
            }
            steps {
                bat "devpi use http://devpy.library.illinois.edu"
                withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                    bat "${tool 'Python3.6.3_Win64'} -m devpi login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                    bat "${tool 'Python3.6.3_Win64'} -m devpi use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                    script {
                        bat "${tool 'Python3.6.3_Win64'} -m devpi upload --from-dir dist"
                        try {
                            bat "${tool 'Python3.6.3_Win64'} -m devpi upload --only-docs"
                        } catch (exc) {
                            echo "Unable to upload to devpi with docs."
                        }
                    }
                }
                // withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                //     bat "${tool 'Python3.6.3_Win64'} -m devpi login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                //     bat "${tool 'Python3.6.3_Win64'} -m devpi use /${DEVPI_USERNAME}/${env.BRANCH_NAME}"
                //     script {
                //         try{
                //             bat "${tool 'Python3.6.3_Win64'} -m devpi upload --with-docs"

                //         } catch (exc) {
                //             echo "Unable to upload to devpi with docs. Trying without"
                //             bat "${tool 'Python3.6.3_Win64'} -m devpi upload"
                //         }
                //     }
                //     bat "devpi test hsw"
                // }

            }
            
            // post {
            //     success {
            //         script {
            //             if(params.JIRA_ISSUE != ""){
            //                     jiraComment body: "Jenkins automated message: A new python package for DevPi was sent to http://devpy.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}", issueKey: "${params.JIRA_ISSUE}"

            //                 }
            //         }
            //     }
            // }
        }
        stage("Test Devpi packages") {
            when {
                expression { params.DEPLOY_DEVPI == true }
            }
            steps {
                parallel(
                        "Source": {
                            script {
                                def name = bat(returnStdout: true, script: "@${tool 'Python3.6.3_Win64'} setup.py --name").trim()
                                def version = bat(returnStdout: true, script: "@${tool 'Python3.6.3_Win64'} setup.py --version").trim()
                                node("Windows") {
                                    withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                                        bat "${tool 'Python3.6.3_Win64'} -m devpi login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                                        bat "${tool 'Python3.6.3_Win64'} -m devpi use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                                        echo "Testing Source package in devpi"
                                        script {
                                             def devpi_test = bat(returnStdout: true, script: "${tool 'Python3.6.3_Win64'} -m devpi test --index http://devpy.library.illinois.edu/${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging ${name} -s tar.gz").trim()
                                             if(devpi_test =~ 'tox command failed') {
                                                error("Tox command failed")
                                            }
                                        }
                                    }
                                }

                            }
                        },
                        "Wheel": {
                            script {
                                def name = bat(returnStdout: true, script: "@${tool 'Python3.6.3_Win64'} setup.py --name").trim()
                                def version = bat(returnStdout: true, script: "@${tool 'Python3.6.3_Win64'} setup.py --version").trim()
                                node("Windows") {
                                    withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                                        bat "${tool 'Python3.6.3_Win64'} -m devpi login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                                        bat "${tool 'Python3.6.3_Win64'} -m devpi use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                                        echo "Testing Whl package in devpi"
                                        script {
                                            def devpi_test =  bat(returnStdout: true, script: "${tool 'Python3.6.3_Win64'} -m devpi test --index http://devpy.library.illinois.edu/${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging ${name} -s whl").trim()
                                            if(devpi_test =~ 'tox command failed') {
                                                error("Tox command failed")
                                            }
                                            
                                        }

                                    }
                                }

                            }
                        }
                )

            }
            post {
                success {
                    echo "it Worked. Pushing file to ${env.BRANCH_NAME} index"
                    script {
                        def name = bat(returnStdout: true, script: "@${tool 'Python3.6.3_Win64'} setup.py --name").trim()
                        def version = bat(returnStdout: true, script: "@${tool 'Python3.6.3_Win64'} setup.py --version").trim()
                        withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                            bat "${tool 'Python3.6.3_Win64'} -m devpi login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                            bat "${tool 'Python3.6.3_Win64'} -m devpi use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                            bat "${tool 'Python3.6.3_Win64'} -m devpi push ${name}==${version} ${DEVPI_USERNAME}/${env.BRANCH_NAME}"
                        }

                    }
                }
            }
        }
        stage("Deploy to SCCM") {
            when {
                expression { params.RELEASE == "Release_to_devpi_and_sccm"}
            }
            steps {
                node("Linux"){
                    unstash "msi"
                    deployStash("msi", "${env.SCCM_STAGING_FOLDER}/${params.PROJECT_NAME}/")
                    input("Push a SCCM release?")
                    deployStash("msi", "${env.SCCM_UPLOAD_FOLDER}")
                }

            }
            // steps {
            //     deployStash("msi", "${env.SCCM_UPLOAD_FOLDER}")
            // }

            post {
                success {
                    script {
                        // unstash "Source"
                        def deployment_request = requestDeploy this, "deployment.yml"
                        echo deployment_request
                        writeFile file: "deployment_request.txt", text: deployment_request
                        archiveArtifacts artifacts: "deployment_request.txt"
                        if(params.JIRA_ISSUE != ""){
                            jiraComment body: "Jenkins automated message: Deployment request has been issue.", issueKey: "${params.JIRA_ISSUE}"

                        }

                    }
                }
            }
        }
        stage("Release to DevPi production") {
            when {
                expression { params.RELEASE != "None" && env.BRANCH_NAME == "master" }
            }
            steps {
                script {
                    def name = bat(returnStdout: true, script: "@${tool 'Python3.6.3_Win64'} setup.py --name").trim()
                    def version = bat(returnStdout: true, script: "@${tool 'Python3.6.3_Win64'} setup.py --version").trim()
                    input("Are you sure you want to push ${name} version ${version} to production? This version cannot be overwritten.")
                    withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                        bat "${tool 'Python3.6.3_Win64'} -m devpi login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                        bat "${tool 'Python3.6.3_Win64'} -m devpi use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                        bat "${tool 'Python3.6.3_Win64'} -m devpi push ${name}==${version} production/release"
                    }

                }
                node("Linux"){
                    updateOnlineDocs url_subdomain: params.URL_SUBFOLDER, stash_name: "HTML Documentation"
                }
            }
            post {
                success {
                    script {
                        if(params.JIRA_ISSUE != ""){
                                jiraComment body: "Jenkins automated message: A new python package for DevPi was sent to http://devpy.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}", issueKey: "${params.JIRA_ISSUE}"

                            }
                    }
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
            post {
                success {
                    script {
                        echo "https://www.library.illinois.edu/dccdocs/${params.URL_SUBFOLDER} updated successfully."
                        if(params.JIRA_ISSUE != ""){
                            jiraComment body: "Jenkins automated message: Online documentation has been updated. https://www.library.illinois.edu/dccdocs/${params.URL_SUBFOLDER}", issueKey: "${params.JIRA_ISSUE}"

                        }
                    }
                }
            }
        }
    }
    post {
        always {
            script {
                def name = bat(returnStdout: true, script: "@${tool 'Python3.6.3_Win64'} setup.py --name").trim()
                def version = bat(returnStdout: true, script: "@${tool 'Python3.6.3_Win64'} setup.py --version").trim()
                withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                    bat "${tool 'Python3.6.3_Win64'} -m devpi remove -y ${name}==${version}"
                }
            }
        }
        success {
            echo "Cleaning up workspace"
            deleteDir()
        }
    }
}
