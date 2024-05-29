def get_fingerprint_template(f):
    try:
        print('Waiting for finger...')

        # Wait for finger to read
        while not f.readImage():
            pass

        # Converts read image to characteristics and stores it in charbuffer 1
        f.convertImage(0x01)

        # Remove finger and wait for the same finger again
        print('Remove finger...')
        time.sleep(2)
        print('Waiting for same finger again...')

        # Wait for finger to read again
        while not f.readImage():
            pass

        # Converts read image to characteristics and stores it in charbuffer 2
        f.convertImage(0x02)

        # Compares the charbuffers
        if f.compareCharacteristics() == 0:
            raise Exception('Fingers do not match.')

        # Downloads the characteristics of template
        template = f.downloadCharacteristics(0x01)

        return template

    except Exception as e:
        print('Failed to get fingerprint template!')
        print('Exception message: ' + str(e))
        return None