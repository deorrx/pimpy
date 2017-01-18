def main():
    file_name = 'text.data'
    with open(file_name, 'wb') as f:
        f.write(b'1234567890')
    with open(file_name, 'r+b') as f:
        f.seek(4, 0)
        f.write(b'ab')

if __name__ == '__main__':
    main()
