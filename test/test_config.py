import pytest 

def test_config_import():
    from msb.imu.IMUConfig import IMUConf
    print(IMUConf)

def test_config_yaml_parse():
    example_config_fpath = "../config/msb/imu.yaml"
    from msb.config.parse import read_yaml_config_file
    conf = read_yaml_config_file(example_config_fpath)
    print(conf)

def test_imu_config_class():
    from msb.imu.IMUConfig import IMUConf
    imu_conf = IMUConf()
    print(imu_conf)

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

def test_argparse_key_value():
    import argparse
    from msb.config.cmdline import KeyValue
    parser = argparse.ArgumentParser()
    parser.add_argument('--params', nargs='*', action = KeyValue)
    args = parser.parse_args("--params key=value1".split())
    assert args.params['key'] == "value1"

def test_argparse():
    from msb.config.cmdline import get_cmdline
    from msb.imu.IMUConfig import IMUConf
    from msb.config.parse import update_config
    imu_conf = IMUConf()
    updated_config = { 'verbose' : True, }
    args = get_cmdline("--print-stdout --params sample_rate_div=31".split()) # should return: {'print_stdout' : True}
    update_config(imu_conf, updated_config)
    update_config(imu_conf, args)
    assert imu_conf.verbose == updated_config['verbose']
    assert imu_conf.print_stdout == args['print_stdout']
    assert imu_conf.sample_rate_div == int(args['sample_rate_div'])

