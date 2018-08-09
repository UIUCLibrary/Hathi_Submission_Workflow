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
//    environment {
//        mypy_args = "--junit-xml=mypy.xml"
//        pytest_args = "--junitxml=reports/junit-{env:OS:UNKNOWN_OS}-{envname}.xml --junit-prefix={env:OS:UNKNOWN_OS}  --basetemp={envtmpdir}"
//    }

    parameters {
        booleanParam(name: "FRESH_WORKSPACE", defaultValue: false, description: "Purge workspace before staring and checking out source")
        string(name: 'JIRA_ISSUE', defaultValue: "", description: 'Jira task to generate about updates.')
        booleanParam(name: "BUILD_DOCS", defaultValue: true, description: "Build documentation")
        booleanParam(name: "TEST_RUN_DOCTEST", defaultValue: true, description: "Test documentation")
        booleanParam(name: "TEST_RUN_PYTEST", defaultValue: true, description: "Run unit tests with PyTest")
        booleanParam(name: "TEST_RUN_MYPY", defaultValue: true, description: "Run MyPy static analysis")
        booleanParam(name: "TEST_RUN_TOX", defaultValue: true, description: "Run Tox Tests")
        booleanParam(name: "TEST_RUN_FLAKE8", defaultValue: true, description: "Run Flake8 static analysis")
//        booleanParam(name: "UNIT_TESTS", defaultValue: true, description: "Run Automated Unit Tests")
//        booleanParam(name: "ADDITIONAL_TESTS", defaultValue: true, description: "Run additional tests")
        booleanParam(name: "DEPLOY_DEVPI", defaultValue: true, description: "Deploy to DevPi on http://devpy.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}")
//        choice(choices: 'None\nRelease_to_devpi_only\nRelease_to_devpi_and_sccm\n', description: "Release the build to production. Only available in the Master branch", name: 'RELEASE')
        booleanParam(name: "UPDATE_DOCS", defaultValue: false, description: "Update the documentation")
        string(name: 'URL_SUBFOLDER', defaultValue: "DCCMedusaPackager", description: 'The directory that the docs should be saved under')
        booleanParam(name: "DEPLOY_DEVPI_PRODUCTION", defaultValue: false, description: "Deploy to https://devpi.library.illinois.edu/production/release")
        // booleanParam(name: "PACKAGE", defaultValue: true, description: "Create a Packages")
        // booleanParam(name: "DEPLOY", defaultValue: false, description: "Deploy SCCM")
//    //////////////////

//        booleanParam(name: "UNIT_TESTS", defaultValue: true, description: "Run automated unit tests")
//        booleanParam(name: "ADDITIONAL_TESTS", defaultValue: true, description: "Run additional tests")
//        booleanParam(name: "PACKAGE", defaultValue: true, description: "Create a package")
        // booleanParam(name: "DEPLOY_SCCM", defaultValue: false, description: "Create SCCM deployment package")
        booleanParam(name: "DEPLOY_DOCS", defaultValue: false, description: "Update online documentation")

    }
    stages {
        stage("Configure"){
            stages{
                stage("Purge all existing data in workspace"){
                    when{
                        equals expected: true, actual: params.FRESH_WORKSPACE
                    }
                    steps{
                        deleteDir()
                        dir("source"){
                            checkout scm
                        }
                    }
                    post{
                        success{
                            bat "dir /s /B"
                        }
                    }
                }

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
                stage("Cleanup"){
                    steps {


                        dir("logs"){
                            deleteDir()
                            echo "Cleaned out logs directory"
                            bat "dir"
                        }

                        dir("build"){
                            deleteDir()
                            echo "Cleaned out build directory"
                            bat "dir"
                        }
                        dir("dist"){
                            deleteDir()
                            echo "Cleaned out dist directory"
                            bat "dir"
                        }

                        dir("reports"){
                            deleteDir()
                            echo "Cleaned out reports directory"
                            bat "dir"
                        }
                    }
                    post{
                        failure {
                            deleteDir()
                        }
                    }
                }
                stage("Installing required system level dependencies"){
                    steps{
                        lock("system_python"){
                            bat "${tool 'CPython-3.6'} -m pip install --upgrade pip --quiet"
                        }
                        tee("logs/pippackages_system_${NODE_NAME}.log") {
                            bat "${tool 'CPython-3.6'} -m pip list"
                        }
                    }
                    post{
                        always{
                            dir("logs"){
                                script{
                                    def log_files = findFiles glob: '**/pippackages_system_*.log'
                                    log_files.each { log_file ->
                                        echo "Found ${log_file}"
                                        archiveArtifacts artifacts: "${log_file}"
                                        bat "del ${log_file}"
                                    }
                                }
                            }
                        }
                        failure {
                            deleteDir()
                        }
                    }
                }
                stage("Creating virtualenv for building"){
                    steps {
                        bat "${tool 'CPython-3.6'} -m venv venv"

                        script {
                            try {
                                bat "call venv\\Scripts\\python.exe -m pip install -U pip"
                            }
                            catch (exc) {
                                bat "${tool 'CPython-3.6'} -m venv venv"
                                bat "call venv\\Scripts\\python.exe -m pip install -U pip --no-cache-dir"
                            }
                        }

                        bat "venv\\Scripts\\pip.exe install -r source\\requirements.txt -r source\\requirements-dev.txt --upgrade-strategy only-if-needed"
                        bat "venv\\Scripts\\pip.exe install devpi-client lxml pytest-cov --upgrade-strategy only-if-needed"



                        tee("logs/pippackages_venv_${NODE_NAME}.log") {
                            bat "venv\\Scripts\\pip.exe list"
                        }
                    }
                    post{
                        always{
                            dir("logs"){
                                script{
                                    def log_files = findFiles glob: '**/pippackages_venv_*.log'
                                    log_files.each { log_file ->
                                        echo "Found ${log_file}"
                                        archiveArtifacts artifacts: "${log_file}"
                                        bat "del ${log_file}"
                                    }
                                }
                            }
                        }
                        failure {
                            deleteDir()
                        }
                    }
                }
                stage("Setting variables used by the rest of the build"){
                    steps{

                        script {
                            // Set up the reports directory variable
                            REPORT_DIR = "${WORKSPACE}\\reports"
                            dir("source"){
                                PKG_NAME = bat(returnStdout: true, script: "@${tool 'CPython-3.6'}  setup.py --name").trim()
                                PKG_VERSION = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --version").trim()
                            }
                        }

                        script{
                            DOC_ZIP_FILENAME = "${PKG_NAME}-${PKG_VERSION}.doc.zip"
                            junit_filename = "junit-${env.NODE_NAME}-${env.GIT_COMMIT.substring(0,7)}-pytest.xml"
                        }




                        script{
                            VENV_ROOT = "${WORKSPACE}\\venv\\"

                            VENV_PYTHON = "${WORKSPACE}\\venv\\Scripts\\python.exe"
                            bat "${VENV_PYTHON} --version"

                            VENV_PIP = "${WORKSPACE}\\venv\\Scripts\\pip.exe"
                            bat "${VENV_PIP} --version"
                        }


                        bat "venv\\Scripts\\devpi use https://devpi.library.illinois.edu"
                        withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                            bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                        }
                        bat "dir"
                    }
                    post{
                        always{
                            echo """Name                            = ${PKG_NAME}
    Version                         = ${PKG_VERSION}
    Report Directory                = ${REPORT_DIR}
    documentation zip file          = ${DOC_ZIP_FILENAME}
    Python virtual environment path = ${VENV_ROOT}
    VirtualEnv Python executable    = ${VENV_PYTHON}
    VirtualEnv Pip executable       = ${VENV_PIP}
    junit_filename                  = ${junit_filename}
    """
                        }
                    }
                }
            }
        }


//        stage("Cloning and Generating Source") {
//            steps {
//                deleteDir()
//                checkout scm
//                // virtualenv python_path: "${tool 'Python3.6.3_Win64'}", requirements_file: "requirements.txt", windows: true, "python setup.py build"
//                bat """${tool 'Python3.6.3_Win64'} -m venv venv
//                    call venv\\Scripts\\activate.bat
//                    pip install -r requirements.txt
//                    pip install -r requirements-dev.txt
//                    python setup.py build
//"""
//                stash includes: '**', name: "Source", useDefaultExcludes: false
//
//                stash includes: 'deployment.yml', name: "Deployment"
//            }
//
//        }
        stage("Building") {
            stages{
                stage("Building Python Package"){
                    steps {
                        tee("logs/build.log") {
                            dir("source"){
                                bat "${WORKSPACE}\\venv\\Scripts\\python.exe setup.py build -b ${WORKSPACE}\\build"
                            }

                        }
                    }
                    post{
                        always{
                            script{
                                def log_files = findFiles glob: '**/*.log'
                                log_files.each { log_file ->
                                    echo "Found ${log_file}"
                                    archiveArtifacts artifacts: "${log_file}"
                                    warnings canRunOnFailed: true, parserConfigurations: [[parserName: 'MSBuild', pattern: "${log_file}"]]
                                    bat "del ${log_file}"
                                }
                            }
                        }
                    }
                }
                stage("Building Sphinx Documentation"){
                    when {
                        equals expected: true, actual: params.BUILD_DOCS
                    }
                    steps {
                        dir("build/docs/html"){
                            deleteDir()
                            echo "Cleaned out build/docs/html dirctory"

                        }
                        script{
                            // Add a line to config file so auto docs look in the build folder
                            def sphinx_config_file = 'source/docs/source/conf.py'
                            def extra_line = "sys.path.insert(0, os.path.abspath('${WORKSPACE}/build/lib'))"
                            def readContent = readFile "${sphinx_config_file}"
                            echo "Adding \"${extra_line}\" to ${sphinx_config_file}."
                            writeFile file: "${sphinx_config_file}", text: readContent+"\r\n${extra_line}\r\n"


                        }
                        echo "Building docs on ${env.NODE_NAME}"
                        tee("logs/build_sphinx.log") {
                            dir("build/lib"){
                                bat "${WORKSPACE}\\venv\\Scripts\\sphinx-build.exe -b html ${WORKSPACE}\\source\\docs\\source ${WORKSPACE}\\build\\docs\\html -d ${WORKSPACE}\\build\\docs\\doctrees"
                            }
                        }
                    }
                    post{
                        always {
                            dir("logs"){
                                script{
                                    def log_files = findFiles glob: '**/*.log'
                                    log_files.each { log_file ->
                                        echo "Found ${log_file}"
                                        archiveArtifacts artifacts: "${log_file}"
                                        bat "del ${log_file}"
                                    }
                                }
                            }
                        }
                        success{
                            publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'build/docs/html', reportFiles: 'index.html', reportName: 'Documentation', reportTitles: ''])
                            dir("${WORKSPACE}/dist"){
                                zip archive: true, dir: "${WORKSPACE}/build/docs/html", glob: '', zipFile: "${DOC_ZIP_FILENAME}"
                            }
                        }
                    }

                }
            }
        }
        stage("Tests") {
            parallel {
                stage("PyTest"){
                    when {
                        equals expected: true, actual: params.TEST_RUN_PYTEST
                    }
                    steps{
                        dir("source"){
                            bat "${WORKSPACE}\\venv\\Scripts\\pytest.exe --junitxml=${WORKSPACE}/reports/junit-${env.NODE_NAME}-pytest.xml --junit-prefix=${env.NODE_NAME}-pytest --cov-report html:${WORKSPACE}/reports/coverage/ --cov=hsw" //  --basetemp={envtmpdir}"
                        }

                    }
                    post {
                        always{
                            dir("reports"){
                                script{
                                    def report_files = findFiles glob: '**/*.pytest.xml'
                                    report_files.each { report_file ->
                                        echo "Found ${report_file}"
                                        // archiveArtifacts artifacts: "${log_file}"
                                        junit "${report_file}"
                                        bat "del ${report_file}"
                                    }
                                }
                            }
                            // junit "reports/junit-${env.NODE_NAME}-pytest.xml"
                            publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'reports/coverage', reportFiles: 'index.html', reportName: 'Coverage', reportTitles: ''])
                        }
                    }
                }
                stage("Doc Test"){
                    when{
                        equals expected: true, actual: params.TEST_RUN_DOCTEST
                    }
                    steps{
                        dir("source"){
                            bat "${WORKSPACE}\\venv\\Scripts\\sphinx-build.exe -b doctest docs\\source ${WORKSPACE}\\build\\docs -d ${WORKSPACE}\\build\\docs\\doctrees -v"
                        }
                    }

                }
                stage("MyPy"){
                    when{
                        equals expected: true, actual: params.TEST_RUN_MYPY
                    }
                    steps{
                        script{
                            try{
                                tee('logs/mypy.log') {
                                    dir("source"){
                                        bat "${WORKSPACE}\\venv\\Scripts\\mypy.exe -p hsw --junit-xml=${WORKSPACE}/junit-${env.NODE_NAME}-mypy.xml --html-report ${WORKSPACE}/reports/mypy_html"
                                    }
                                }
                            } catch (exc) {
                                echo "MyPy found some warnings"
                            }
                        }
                    }
                    post{
                        always {
                            junit "junit-${env.NODE_NAME}-mypy.xml"
                            warnings canRunOnFailed: true, parserConfigurations: [[parserName: 'MyPy', pattern: 'logs/mypy.log']], unHealthy: ''
                            publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'reports/mypy_html', reportFiles: 'index.html', reportName: 'MyPy', reportTitles: ''])
                        }
                    }
                }
                stage("Run Tox test") {
                    when{
                        equals expected: true, actual: params.TEST_RUN_TOX
                    }
                    steps {
                        dir("source"){
                            script{
                                try{
                                    bat "pipenv run tox --workdir ${WORKSPACE}\\.tox"
                                } catch (exc) {
                                    bat "pipenv run tox --workdir ${WORKSPACE}\\.tox --recreate"
                                }
                            }

                        }
                    }
                }
                stage("Run Flake8 Static Analysis") {
                    when {
                        equals expected: true, actual: params.TEST_RUN_FLAKE8
                    }
                    steps{
                        script{
                            try{
                                tee('reports/flake8.log') {
                                    dir("source"){
                                        bat "${WORKSPACE}\\venv\\Scripts\\flake8.exe hsw --format=pylint"
                                    }
                                }
                            } catch (exc) {
                                echo "flake8 found some warnings"
                            }
                        }
                    }
                    post {
                        always {
                            script {
                                dir("reports"){

                                    def linter_logs = findFiles glob: "**/flake8.log"
                                    linter_logs.each { linter_log ->
                                        echo "Found ${linter_log}"
                                        archiveArtifacts artifacts: "${linter_log}"
                                        warnings canRunOnFailed: true, parserConfigurations: [[parserName: 'PyLint', pattern: "${linter_log}"]], unHealthy: ''
                                        bat "del ${linter_log}"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

//        stage("Unit tests") {
//            when {
//                expression { params.UNIT_TESTS == true }
//            }
//            steps {
//                parallel(
//                        "Windows": {
//                            script {
//                                def runner = new Tox(this)
//                                runner.env = "pytest"
//                                runner.windows = true
//                                runner.stash = "Source"
//                                runner.label = "Windows"
//                                runner.post = {
//                                    junit 'reports/junit-*.xml'
//                                }
//                                runner.run()
//                            }
//                        }
//                        // "Windows": {
//                        //     node(label: 'Windows') {
//                        //         deleteDir()
//                        //         unstash "Source"
//                        //         bat "${env.TOX}  -e pytest"
//                        //         junit 'reports/junit-*.xml'
//                        //
//                        //     }
//                        // }
//                        // "Linux": {
//                        //     node(label: "!Windows") {
//                        //         deleteDir()
//                        //         unstash "Source"
//                        //         withEnv(["PATH=${env.PYTHON3}/..:${env.PATH}"]) {
//                        //             sh "${env.TOX}  -e pytest"
//                        //         }
//                        //         junit 'reports/junit-*.xml'
//                        //     }
//                        // }
//                )
//            }
//        }
//        stage("Additional tests") {
//            when {
//                expression { params.ADDITIONAL_TESTS == true }
//            }
//
//            steps {
//                parallel(
//                        "Documentation": {
//                            script {
//                                def runner = new Tox(this)
//                                runner.env = "docs"
//                                runner.windows = true
//                                // runner.windows = false
//                                runner.stash = "Source"
//                                // runner.label = "Linux"
//                                runner.label = "Windows"
//                                runner.post = {
//                                    dir('.tox/dist/html/') {
//                                        stash includes: '**', name: "HTML Documentation", useDefaultExcludes: false
//                                    }
//                                }
//                                runner.run()
//
//                            }
//                        },
//                        "MyPy": {
//                            script {
//                                def runner = new Tox(this)
//                                runner.env = "mypy"
//                                runner.windows = false
//                                runner.stash = "Source"
//                                runner.label = "Linux"
//                                runner.post = {
//                                    junit 'mypy.xml'
//                                }
//                                runner.run()
//
//                            }
//
//                        }
//                )
//            }
//        }

//        stage("Packaging") {
//            when {
//                expression { params.PACKAGE == true }
//            }
//
//            steps {
//                parallel(
//                        "Windows Standalone": {
//                            node(label: "Windows&&VS2015&&DevPi") {
//                                deleteDir()
//                                unstash "Source"
//                                bat "call make.bat release"
////                                bat """${tool 'Python3.6.3_Win64'} -m venv .env
////                                        call .env/Scripts/activate.bat
////                                        pip install --upgrade pip setuptools
////                                        pip install -r requirements.txt
////                                        call make.bat release
////                                       IF NOT %ERRORLEVEL% == 0 (
////                                         echo ABORT: %ERRORLEVEL%
////                                         exit /b %ERRORLEVEL%
////                                       )
////                                    """
//
//
//                                dir("dist") {
//                                    archiveArtifacts artifacts: "*.msi*", fingerprint: true
//                                    stash includes: "*.msi", name: "msi"
//                                }
//                            }
//                        },
//                        "Source and Wheel formats": {
//                            bat """${tool 'Python3.6.3_Win64'} -m venv venv
//                                    call venv\\Scripts\\activate.bat
//                                    pip install -r requirements.txt
//                                    pip install -r requirements-dev.txt
//                                    python setup.py sdist bdist_wheel
//                                    """
//                        }
////                         "Windows Wheel": {
////                             node(label: "Windows") {
////                                 deleteDir()
////                                 unstash "Source"
////                                 bat "${tool 'Python3.6.3_Win64'} setup.py bdist_wheel"
////                                 archiveArtifacts artifacts: "dist/**", fingerprint: true
////                             }
////                         },
//
////                         "Source Release": {
////                             node(label: "Windows") {
////                                 deleteDir()
////                                 unstash "Source"
////                                 bat "${tool 'Python3.6.3_Win64'} setup.py sdist"
////                                 archiveArtifacts artifacts: "dist/**", fingerprint: true
////                             }
//// //                            node(label: Linux) {
//// //                                createSourceRelease(env.PYTHON3, "Source")
//// //                            }
//
////                         }
//                )
//            }
//            post {
//              success {
//                  dir("dist"){
//                      unstash "msi"
//                      archiveArtifacts artifacts: "*.whl", fingerprint: true
//                      archiveArtifacts artifacts: "*.tar.gz", fingerprint: true
//                      archiveArtifacts artifacts: "*.msi", fingerprint: true
//                }
//              }
//            }
//        }

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
        stage("Packaging") {
            when {
                expression { params.DEPLOY_DEVPI == true || params.RELEASE != "None"}
            }
            parallel {
                stage("Source and Wheel formats"){
                    steps{
                        dir("source"){
                            bat "${WORKSPACE}\\venv\\scripts\\python.exe setup.py sdist -d ${WORKSPACE}\\dist bdist_wheel -d ${WORKSPACE}\\dist"
                        }

                    }
                    post{
                        success{
                            dir("dist"){
                                archiveArtifacts artifacts: "*.whl", fingerprint: true
                                archiveArtifacts artifacts: "*.tar.gz", fingerprint: true
                            }
                        }
                    }
                }
                stage("Windows CX_Freeze MSI"){
                    agent{
                        node {
                            label "Windows"
                        }
                    }
                    options {
                        skipDefaultCheckout true
                    }
                    steps{
                        bat "dir"
                        deleteDir()
                        bat "dir"
                        checkout scm
                        bat "dir /s / B"
                        bat "${tool 'CPython-3.6'} -m venv venv"
                        bat "venv\\Scripts\\python.exe -m pip install -U pip>=18.0"
                        bat "venv\\Scripts\\pip.exe install -U setuptools"
                        bat "venv\\Scripts\\pip.exe install cx_freeze appdirs"
                        bat "venv\\Scripts\\pip.exe install -r requirements.txt -r requirements-dev.txt"
                        bat "venv\\Scripts\\python.exe cx_setup.py bdist_msi --add-to-path=true -k --bdist-dir build/msi"
                        // bat "make freeze"


                    }
                    post{
                        success{
                            dir("dist") {
                                stash includes: "*.msi", name: "msi"
                                archiveArtifacts artifacts: "*.msi", fingerprint: true
                            }
                        }
                        cleanup{
                            bat "dir"
                            deleteDir()
                            bat "dir"
                        }
                    }
                }
            }
        }
//        stage("Deploying to Devpi staging") {
//            when {
//                expression { params.DEPLOY_DEVPI == true }
//            }
//            steps {
//                bat "devpi use http://devpy.library.illinois.edu"
//                withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
//                    bat "${tool 'Python3.6.3_Win64'} -m devpi login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
//                    bat "${tool 'Python3.6.3_Win64'} -m devpi use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
//                    script {
//                        bat "${tool 'Python3.6.3_Win64'} -m devpi upload --from-dir dist"
//                        try {
//                            bat "${tool 'Python3.6.3_Win64'} -m devpi upload --only-docs"
//                        } catch (exc) {
//                            echo "Unable to upload to devpi with docs."
//                        }
//                    }
//                }
//                // withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
//                //     bat "${tool 'Python3.6.3_Win64'} -m devpi login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
//                //     bat "${tool 'Python3.6.3_Win64'} -m devpi use /${DEVPI_USERNAME}/${env.BRANCH_NAME}"
//                //     script {
//                //         try{
//                //             bat "${tool 'Python3.6.3_Win64'} -m devpi upload --with-docs"
//
//                //         } catch (exc) {
//                //             echo "Unable to upload to devpi with docs. Trying without"
//                //             bat "${tool 'Python3.6.3_Win64'} -m devpi upload"
//                //         }
//                //     }
//                //     bat "devpi test hsw"
//                // }
//
//            }
//
//            // post {
//            //     success {
//            //         script {
//            //             if(params.JIRA_ISSUE != ""){
//            //                     jiraComment body: "Jenkins automated message: A new python package for DevPi was sent to http://devpy.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}", issueKey: "${params.JIRA_ISSUE}"
//
//            //                 }
//            //         }
//            //     }
//            // }
//        }
//        stage("Test Devpi packages") {
//            when {
//                expression { params.DEPLOY_DEVPI == true }
//            }
//            steps {
//                parallel(
//                        "Source": {
//                            script {
//                                def name = bat(returnStdout: true, script: "@${tool 'Python3.6.3_Win64'} setup.py --name").trim()
//                                def version = bat(returnStdout: true, script: "@${tool 'Python3.6.3_Win64'} setup.py --version").trim()
//                                node("Windows") {
//                                    withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
//                                        bat "${tool 'Python3.6.3_Win64'} -m devpi login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
//                                        bat "${tool 'Python3.6.3_Win64'} -m devpi use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
//                                        echo "Testing Source package in devpi"
//                                        script {
//                                             def devpi_test = bat(returnStdout: true, script: "${tool 'Python3.6.3_Win64'} -m devpi test --index http://devpy.library.illinois.edu/${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging ${name} -s tar.gz").trim()
//                                             if(devpi_test =~ 'tox command failed') {
//                                                error("Tox command failed")
//                                            }
//                                        }
//                                    }
//                                }
//
//                            }
//                        },
//                        "Wheel": {
//                            script {
//                                def name = bat(returnStdout: true, script: "@${tool 'Python3.6.3_Win64'} setup.py --name").trim()
//                                def version = bat(returnStdout: true, script: "@${tool 'Python3.6.3_Win64'} setup.py --version").trim()
//                                node("Windows") {
//                                    withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
//                                        bat "${tool 'Python3.6.3_Win64'} -m devpi login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
//                                        bat "${tool 'Python3.6.3_Win64'} -m devpi use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
//                                        echo "Testing Whl package in devpi"
//                                        script {
//                                            def devpi_test =  bat(returnStdout: true, script: "${tool 'Python3.6.3_Win64'} -m devpi test --index http://devpy.library.illinois.edu/${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging ${name} -s whl").trim()
//                                            if(devpi_test =~ 'tox command failed') {
//                                                error("Tox command failed")
//                                            }
//
//                                        }
//
//                                    }
//                                }
//
//                            }
//                        }
//                )
//
//            }
//            post {
//                success {
//                    echo "it Worked. Pushing file to ${env.BRANCH_NAME} index"
//                    script {
//                        def name = bat(returnStdout: true, script: "@${tool 'Python3.6.3_Win64'} setup.py --name").trim()
//                        def version = bat(returnStdout: true, script: "@${tool 'Python3.6.3_Win64'} setup.py --version").trim()
//                        withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
//                            bat "${tool 'Python3.6.3_Win64'} -m devpi login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
//                            bat "${tool 'Python3.6.3_Win64'} -m devpi use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
//                            bat "${tool 'Python3.6.3_Win64'} -m devpi push ${name}==${version} ${DEVPI_USERNAME}/${env.BRANCH_NAME}"
//                        }
//
//                    }
//                }
//            }
//        }
//        stage("Deploy to SCCM") {
//            when {
//                expression { params.RELEASE == "Release_to_devpi_and_sccm"}
//            }
//            steps {
//                node("Linux"){
//                    unstash "msi"
//                    deployStash("msi", "${env.SCCM_STAGING_FOLDER}/${params.PROJECT_NAME}/")
//                    input("Push a SCCM release?")
//                    deployStash("msi", "${env.SCCM_UPLOAD_FOLDER}")
//                }
//
//            }
//            // steps {
//            //     deployStash("msi", "${env.SCCM_UPLOAD_FOLDER}")
//            // }
//
//            post {
//                success {
//                    script {
//                        // unstash "Source"
//                        def deployment_request = requestDeploy this, "deployment.yml"
//                        echo deployment_request
//                        writeFile file: "deployment_request.txt", text: deployment_request
//                        archiveArtifacts artifacts: "deployment_request.txt"
//                        if(params.JIRA_ISSUE != ""){
//                            jiraComment body: "Jenkins automated message: Deployment request has been issue.", issueKey: "${params.JIRA_ISSUE}"
//
//                        }
//
//                    }
//                }
//            }
//        }
        stage("Deploying to DevPi staging") {
            when {
                allOf{
                    equals expected: true, actual: params.DEPLOY_DEVPI
                    anyOf {
                        equals expected: "master", actual: env.BRANCH_NAME
                        equals expected: "dev", actual: env.BRANCH_NAME
                    }
                }
            }
            steps {
                bat "venv\\Scripts\\devpi.exe use http://devpy.library.illinois.edu"
                withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                    bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                    bat "venv\\Scripts\\devpi.exe use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                    script {
                        bat "venv\\Scripts\\devpi.exe upload --from-dir dist"
                        try {
//                            bat "venv\\Scripts\\devpi.exe upload --only-docs"
                            bat "venv\\Scripts\\devpi.exe upload --only-docs ${WORKSPACE}\\dist\\${DOC_ZIP_FILENAME}"
                        } catch (exc) {
                            echo "Unable to upload to devpi with docs."
                        }
                    }
                }

            }
        }
        stage("Test Devpi packages") {
            when {
                allOf{
                    equals expected: true, actual: params.DEPLOY_DEVPI
                    anyOf {
                        equals expected: "master", actual: env.BRANCH_NAME
                        equals expected: "dev", actual: env.BRANCH_NAME
                    }
                }
            }
//            steps {
            parallel {
                stage("Source Distribution: .tar.gz") {
                    steps {
                        echo "Testing Source tar.gz package in DevPi"
                        withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                            bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"

                        }
                        bat "venv\\Scripts\\devpi.exe use /DS_Jenkins/${env.BRANCH_NAME}_staging"

                        script {
                            def devpi_test_return_code = bat returnStatus: true, script: "venv\\Scripts\\devpi.exe test --index https://devpi.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}_staging ${PKG_NAME} -s tar.gz  --verbose"
                            if(devpi_test_return_code != 0){
                                error "Devpi exit code for tar.gz was ${devpi_test_return_code}"
                            }
                        }
                        echo "Finished testing Source Distribution: .tar.gz"
                    }
                    post {
                        failure {
                            echo "Tests for .tar.gz source on DevPi failed."
                        }
                    }

                }
                stage("Source Distribution: .zip") {
                    steps {
                        echo "Testing Source zip package in DevPi"
                        withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                            bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                        }
                        bat "venv\\Scripts\\devpi.exe use /DS_Jenkins/${env.BRANCH_NAME}_staging"
                        script {
                            def devpi_test_return_code = bat returnStatus: true, script: "venv\\Scripts\\devpi.exe test --index https://devpi.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}_staging ${PKG_NAME} -s zip --verbose"
                            if(devpi_test_return_code != 0){
                                error "Devpi exit code for zip was ${devpi_test_return_code}"
                            }
                        }
                        echo "Finished testing Source Distribution: .zip"
                    }
                    post {
                        failure {
                            echo "Tests for .zip source on DevPi failed."
                        }
                    }
                }
                stage("Built Distribution: .whl") {
                    agent {
                        node {
                            label "Windows && Python3"
                        }
                    }
                    options {
                        skipDefaultCheckout()
                    }
                    steps {
                        echo "Testing Whl package in devpi"
                        bat "${tool 'CPython-3.6'} -m venv venv"
                        bat "venv\\Scripts\\pip.exe install tox devpi-client"
                        withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                            bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                        }
                        bat "venv\\Scripts\\devpi.exe use /DS_Jenkins/${env.BRANCH_NAME}_staging"
                        script{
                            def devpi_test_return_code = bat returnStatus: true, script: "venv\\Scripts\\devpi.exe test --index https://devpi.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}_staging ${PKG_NAME} -s whl  --verbose"
                            if(devpi_test_return_code != 0){
                                error "Devpi exit code for whl was ${devpi_test_return_code}"
                            }
                        }
                        echo "Finished testing Built Distribution: .whl"
                    }
                    post {
                        failure {
                            echo "Tests for whl on DevPi failed."
                        }
                    }
                }
            }

            post {
                success {
                    echo "it Worked. Pushing file to ${env.BRANCH_NAME} index"
                    script {
                        withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                            bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                            bat "venv\\Scripts\\devpi.exe use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                            bat "venv\\Scripts\\devpi.exe push ${PKG_NAME}==${PKG_VERSION} ${DEVPI_USERNAME}/${env.BRANCH_NAME}"
                        }
                    }
                }
            }
        }
//        stage("Release to DevPi production") {
//            when {
//                expression { params.RELEASE != "None" && env.BRANCH_NAME == "master" }
//            }
//            steps {
//                script {
//                    def name = bat(returnStdout: true, script: "@${tool 'Python3.6.3_Win64'} setup.py --name").trim()
//                    def version = bat(returnStdout: true, script: "@${tool 'Python3.6.3_Win64'} setup.py --version").trim()
//                    input("Are you sure you want to push ${name} version ${version} to production? This version cannot be overwritten.")
//                    withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
//                        bat "${tool 'Python3.6.3_Win64'} -m devpi login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
//                        bat "${tool 'Python3.6.3_Win64'} -m devpi use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
//                        bat "${tool 'Python3.6.3_Win64'} -m devpi push ${name}==${version} production/release"
//                    }
//
//                }
//                node("Linux"){
//                    updateOnlineDocs url_subdomain: params.URL_SUBFOLDER, stash_name: "HTML Documentation"
//                }
//            }
//            post {
//                success {
//                    script {
//                        if(params.JIRA_ISSUE != ""){
//                                jiraComment body: "Jenkins automated message: A new python package for DevPi was sent to http://devpy.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}", issueKey: "${params.JIRA_ISSUE}"
//
//                            }
//                    }
//                }
//            }
//        }
        
//        stage("Update online documentation") {
//            agent any
//            when {
//                expression { params.UPDATE_DOCS == true }
//            }
//
//            steps {
//                deleteDir()
//                script {
//                    updateOnlineDocs url_subdomain: params.URL_SUBFOLDER, stash_name: "HTML Documentation"
//
//                }
//            }
//            post {
//                success {
//                    script {
//                        echo "https://www.library.illinois.edu/dccdocs/${params.URL_SUBFOLDER} updated successfully."
//                        if(params.JIRA_ISSUE != ""){
//                            jiraComment body: "Jenkins automated message: Online documentation has been updated. https://www.library.illinois.edu/dccdocs/${params.URL_SUBFOLDER}", issueKey: "${params.JIRA_ISSUE}"
//
//                        }
//                    }
//                }
//            }
//        }
    stage("Deploy"){
            parallel {
                stage("Deploy Online Documentation") {
                    when{
                        equals expected: true, actual: params.DEPLOY_DOCS
                    }
                    steps{
                        dir("build/docs/html/"){
                            input 'Update project documentation?'
                            sshPublisher(
                                publishers: [
                                    sshPublisherDesc(
                                        configName: 'apache-ns - lib-dccuser-updater',
                                        sshLabel: [label: 'Linux'],
                                        transfers: [sshTransfer(excludes: '',
                                        execCommand: '',
                                        execTimeout: 120000,
                                        flatten: false,
                                        makeEmptyDirs: false,
                                        noDefaultExcludes: false,
                                        patternSeparator: '[, ]+',
                                        remoteDirectory: "${params.DEPLOY_DOCS_URL_SUBFOLDER}",
                                        remoteDirectorySDF: false,
                                        removePrefix: '',
                                        sourceFiles: '**')],
                                    usePromotionTimestamp: false,
                                    useWorkspaceInPromotion: false,
                                    verbose: true
                                    )
                                ]
                            )
                        }
                    }
                }
                stage("Deploy standalone to Hathi tools Beta"){
                    when {
                        allOf{
                            equals expected: true, actual: params.DEPLOY_HATHI_TOOL_BETA
                            equals expected: true, actual: params.PACKAGE_WINDOWS_STANDALONE
                        }
                    }
                    steps {
                        unstash "standalone_installer"
                        input 'Update standalone to //storage.library.illinois.edu/HathiTrust/Tools/beta/?'
                        cifsPublisher(
                                    publishers: [[
                                        configName: 'hathitrust tools',
                                        transfers: [[
                                            cleanRemote: false,
                                            excludes: '',
                                            flatten: false,
                                            makeEmptyDirs: false,
                                            noDefaultExcludes: false,
                                            patternSeparator: '[, ]+',
                                            remoteDirectory: 'beta',
                                            remoteDirectorySDF: false,
                                            removePrefix: '',
                                            sourceFiles: '*.msi'
                                            ]],
                                        usePromotionTimestamp: false,
                                        useWorkspaceInPromotion: false,
                                        verbose: false
                                        ]]
                                )
                    }
                }
                stage("Deploy to DevPi Production") {
                    when {
                        allOf{
                            equals expected: true, actual: params.DEPLOY_DEVPI_PRODUCTION
                            equals expected: true, actual: params.DEPLOY_DEVPI
                            branch "master"
                        }
                    }
                    steps {
                        script {
                            // def name = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --name").trim()
                            // def version = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --version").trim()
                            input "Release ${PKG_NAME} ${PKG_VERSION} to DevPi Production?"
                            withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                                bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                                bat "venv\\Scripts\\devpi.exe use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                                bat "venv\\Scripts\\devpi.exe push ${PKG_NAME}==${PKG_VERSION} production/release"
                            }
                        }
                    }
                }
                stage("Deploy Standalone Build to SCCM") {
                    when {
                        allOf{
                            equals expected: true, actual: params.DEPLOY_SCCM
                            equals expected: true, actual: params.PACKAGE_WINDOWS_STANDALONE
                            branch "master"
                        }
                        // expression { params.RELEASE == "Release_to_devpi_and_sccm"}
                    }

                    steps {
                        unstash "msi"
                        unstash "Deployment"
                        script{
                            // def name = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --name").trim()
                            def msi_files = findFiles glob: '*.msi'

                            def deployment_request = requestDeploy yaml: "deployment.yml", file_name: msi_files[0]
                            cifsPublisher(
                                publishers: [[
                                    configName: 'SCCM Staging',
                                    transfers: [[
                                        cleanRemote: false,
                                        excludes: '',
                                        flatten: false,
                                        makeEmptyDirs: false,
                                        noDefaultExcludes: false,
                                        patternSeparator: '[, ]+',
                                        remoteDirectory: '',
                                        remoteDirectorySDF: false,
                                        removePrefix: '',
                                        sourceFiles: '*.msi'
                                        ]],
                                    usePromotionTimestamp: false,
                                    useWorkspaceInPromotion: false,
                                    verbose: false
                                    ]]
                                )

                            // deployStash("msi", "${env.SCCM_STAGING_FOLDER}/${name}/")

                            input("Deploy to production?")
                            writeFile file: "deployment_request.txt", text: deployment_request
                            echo deployment_request
                            cifsPublisher(
                                publishers: [[
                                    configName: 'SCCM Upload',
                                    transfers: [[
                                        cleanRemote: false,
                                        excludes: '',
                                        flatten: false,
                                        makeEmptyDirs: false,
                                        noDefaultExcludes: false,
                                        patternSeparator: '[, ]+',
                                        remoteDirectory: '',
                                        remoteDirectorySDF: false,
                                        removePrefix: '',
                                        sourceFiles: '*.msi'
                                        ]],
                                    usePromotionTimestamp: false,
                                    useWorkspaceInPromotion: false,
                                    verbose: false
                                    ]]
                            )
                            // deployStash("msi", "${env.SCCM_UPLOAD_FOLDER}")
                        }
                    }
                    post {
                        success {
                            archiveArtifacts artifacts: "deployment_request.txt"
                        }
                    }
                }
            }
        }
    }
     post {
        cleanup{
            script {
                if(fileExists('source/setup.py')){
                    dir("source"){
                        try{
                            retry(3) {
                                bat "${WORKSPACE}\\venv\\Scripts\\python.exe setup.py clean --all"
                            }
                        } catch (Exception ex) {
                            echo "Unable to successfully run clean. Purging source directory."
                            deleteDir()
                        }
                    }
                }
                bat "dir"
                if (env.BRANCH_NAME == "master" || env.BRANCH_NAME == "dev"){
                    withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                        bat "venv\\Scripts\\devpi.exe login DS_Jenkins --password ${DEVPI_PASSWORD}"
                        bat "venv\\Scripts\\devpi.exe use /DS_Jenkins/${env.BRANCH_NAME}_staging"
                    }

                    def devpi_remove_return_code = bat returnStatus: true, script:"venv\\Scripts\\devpi.exe remove -y ${PKG_NAME}==${PKG_VERSION}"
                    echo "Devpi remove exited with code ${devpi_remove_return_code}."
                }
            }
        }
    }
//    post {
//        always {
//            script {
//                def name = bat(returnStdout: true, script: "@${tool 'Python3.6.3_Win64'} setup.py --name").trim()
//                def version = bat(returnStdout: true, script: "@${tool 'Python3.6.3_Win64'} setup.py --version").trim()
//                withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
//                    bat "${tool 'Python3.6.3_Win64'} -m devpi remove -y ${name}==${version}"
//                }
//            }
//        }
//        success {
//            echo "Cleaning up workspace"
//            deleteDir()
//        }
//    }
}
