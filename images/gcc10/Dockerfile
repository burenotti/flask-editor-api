FROM gcc:10

RUN useradd -M -d /sandbox sandbox && \
    mkdir /sandbox && \
    chown -R sandbox:sandbox /sandbox && \
    useradd -M -d /build builder && \
    mkdir /build && \
    chown -R builder:builder /build
