FROM golang:1.18-buster as builder

WORKDIR /app
ADD . ./

RUN go build -o /arunapi

FROM gcr.io/distroless/base-debian10

WORKDIR /

COPY --from=builder /arunapi /arunapi

ENV PORT 8080
ENV GIN_MODE release

EXPOSE 8080

USER nonroot:nonroot

ENTRYPOINT ["/arunapi"]
