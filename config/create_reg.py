import src.apollo_config as config

# the windows registry doesn't expand environment variables in REG_SZ (string values).  REG_MULTI_SZ does,
# but for some stupid reason the serialized representation is binary and thus very hard to work with.

# as a compromise, i use REG_SZ, and then expand the APOLLO env var myself

p = str(config.APOLLO_PATH).replace("\\", "\\\\")
with open('shell extentions.pre','r') as finput:
    with open('shell extentions.reg','w') as foutput:
        foutput.write(finput.read().replace("%APOLLO%",p))


