import pytest 

def test_config_import():
    from msb.imu.IMUConfig import IMUConf

def test_config_yaml_parse():
    example_config_fpath = "../config/msb/imu.yaml"
    from msb.config.parse import read_yaml_config_file
    conf = read_yaml_config_file(example_config_fpath)

def test_imu_config_class():
    from msb.imu.IMUConfig import IMUConf
    imu_conf = IMUConf()

def test_update_config_class():
    from msb.imu.IMUConfig import IMUConf
    from msb.config.parse import update_config
    updated_config = {
        'verbose' : True,        
    }
    imu_conf = IMUConf()
    imu_conf.verbose = False
    update_config(imu_conf, updated_config)
    assert imu_conf.verbose == updated_config['verbose']


def test_attribute_does_not_exists_warning():
    from msb.imu.IMUConfig import IMUConf
    from msb.config.parse import update_config
    updated_config = {
        'does_not_exist' : 42,        
    }
    imu_conf = IMUConf()
    with pytest.warns(UserWarning):
        update_config(imu_conf, updated_config)
    #assert imu_conf.verbose == updated_config['verbose']
    
