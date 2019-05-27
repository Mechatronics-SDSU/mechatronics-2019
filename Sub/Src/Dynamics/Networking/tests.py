from Writer import Writer as WriteClass
from Reader import Reader as ReadClass
import io

#writer = WriteClass(b"12", b"Hello World")
#writer.write("Hey") throws errors
#writer.write()
#writer.write_to_file("tests.txt", b"Chelsea sucks")


buffer = io.BytesIO(b"Hi, my name is Shafi, and I want this program to work. That would be nice")
reader = ReadClass(b"Hello", buffer)
print(reader.read(32))
