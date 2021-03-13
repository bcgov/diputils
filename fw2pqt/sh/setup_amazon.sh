# setup for amazon linux. From https://arrow.apache.org/install/
sudo yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
sudo yum install -y https://apache.bintray.com/arrow/centos/7/apache-arrow-release-latest.rpm
sudo yum install -y --enablerepo=epel arrow-devel # For C++
sudo yum install -y --enablerepo=epel arrow-glib-devel # For GLib (C)
sudo yum install -y --enablerepo=epel arrow-dataset-devel # For Arrow Dataset C++
sudo yum install -y --enablerepo=epel parquet-devel # For Apache Parquet C++
sudo yum install -y --enablerepo=epel parquet-glib-devel # For Parquet GLib (C)
