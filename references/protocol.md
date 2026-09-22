# TRACK=PROTOCOL

1 采样 PCAP/hook  2 分帧（长度/分隔/magic） 3 字段（类型/端序/语义/变化）
4 校验和（CRC/sum/xor/z3） 5 序列化（pb/msgpack/TLV） 6 状态机 7 parse→serialize byte-equal

交付：字段表 + parser/serializer（python）+ Lua dissector。TCP 必须处理粘包半包。长度字段测 0/max/不符。
