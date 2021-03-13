# setup for centos 8 or red had enterprise linux 8. From https://arrow.apache.org/install/
sudo dnf install -y epel-release || sudo dnf install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-$(cut -d: -f5 /etc/system-release-cpe | cut -d. -f1).noarch.rpm
sudo dnf install -y https://apache.bintray.com/arrow/centos/$(cut -d: -f5 /etc/system-release-cpe | cut -d. -f1)/apache-arrow-release-latest.rpm
sudo dnf config-manager --set-enabled epel || :
sudo dnf config-manager --set-enabled powertools || :
sudo dnf config-manager --set-enabled codeready-builder-for-rhel-$(cut -d: -f5 /etc/system-release-cpe | cut -d. -f1)-rhui-rpms || :
sudo subscription-manager repos --enable codeready-builder-for-rhel-$(cut -d: -f5 /etc/system-release-cpe | cut -d. -f1)-$(arch)-rpms || :
sudo dnf install -y arrow-devel # For C++
sudo dnf install -y arrow-glib-devel # For GLib (C)
sudo dnf install -y arrow-dataset-devel # For Arrow Dataset C++
sudo dnf install -y parquet-devel # For Apache Parquet C++
sudo dnf install -y parquet-glib-devel # For Parquet GLib (C)
