# Install remotes if not already installed
if (!require("remotes")) {
    install.packages("remotes", repos="https://cloud.r-project.org/")
}

# Install Delphi packages
remotes::install_github("cmu-delphi/epidatr", ref = "main")
install.packages(c("epiprocess", "epidatasets", "epipredict"), 
                repos=c("https://cmu-delphi.github.io/delphi.github.io/r", 
                       "https://cloud.r-project.org/"), 
                dependencies=TRUE)
