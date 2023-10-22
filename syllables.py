#!/usr/local/bin/python
# -*- coding: utf8 -*-
import codecs, sys, os, math, argparse

JLT="ㄱ,ㄲ,ㄴ,ㄷ,ㄸ,ㄹ,ㅁ,ㅂ,ㅃ,ㅅ,ㅆ,ㅇ,ㅈ,ㅉ,ㅊ,ㅋ,ㅌ,ㅍ,ㅎ".split(",")
JTT=",ㄱ,ㄲ,ㄱㅅ,ㄴ,ㄴㅈ,ㄴㅎ,ㄷ,ㄹ,ㄹㄱ,ㄹㅁ,ㄹㅂ,ㄹㅅ,ㄹㅌ,ㄹㅍ,ㄹㅎ,ㅁ,ㅂ,ㅂㅅ,ㅅ,ㅆ,ㅇ,ㅈ,ㅊ,ㅋ,ㅌ,ㅍ,ㅎ".split(",")
JVT="ㅏ,ㅐ,ㅑ,ㅒ,ㅓ,ㅔ,ㅕ,ㅖ,ㅗ,ㅘ,ㅙ,ㅚ,ㅛ,ㅜ,ㅝ,ㅞ,ㅟ,ㅠ,ㅡ,ㅢ,ㅣ".split(",")
SBase=0xAC00
SCount=11172
TCount=28
NCount=588

def HangulName(a):
	b=a.encode().decode('utf8')
	sound=''
	for i in b:
		cp=ord(i)
		SIndex = cp - SBase
		if (0 > SIndex or SIndex >= SCount):
			pass
		
		try:
			LIndex = int(math.floor(SIndex / NCount))
			VIndex = int(math.floor((SIndex % NCount) / TCount))
			TIndex = int(SIndex % TCount)
			sound=sound+(JLT[LIndex] + JVT[VIndex] + JTT[TIndex]).lower()
		except Exception as err:
			pass
	return sound

if "__main__" in __name__:
	parser = argparse.ArgumentParser(description = "Decompose Korean Hangul Syllables")
	parser.add_argument("name", help = "Input of Korean Text", type = str)
	args = parser.parse_args()

	name = args.name
	result = HangulName(name)
	print(result)