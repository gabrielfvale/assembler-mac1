   bipush 5
	 istore x
	 iload x
	 bipush 5
	 if_icmpeq l1
	 bipush 66
	 bipush 77
	 iadd
	 istore c
	 goto l2
l1 iload x
	 bipush 7
	 iadd
	 istore x
l2 bipush 3
