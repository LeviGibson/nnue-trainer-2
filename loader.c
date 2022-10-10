#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <string.h>
#include <stdint.h>

int BATCH_SIZE = -1;
#define MAX_LINE_LENGTH 100
#define FEATURE_COUNT (768*2)
#define WHITE 1
#define BLACK 0
enum {p_P, p_N, p_B, p_R, p_Q, p_K, p_p, p_n, p_b, p_r, p_q, p_k};
const int32_t FLIP_PIECE[12] = {p_p, p_n, p_b, p_r, p_q, p_k, p_P, p_N, p_B, p_R, p_Q, p_K};

const int32_t flip[64] = {
        56, 57, 58, 59, 60, 61, 62, 63,
        48, 49, 50, 51, 52, 53, 54, 55,
        40, 41, 42, 43, 44, 45, 46, 47,
        32, 33, 34, 35, 36, 37, 38, 39,
        24, 25, 26, 27, 28, 29, 30, 31,
        16, 17, 18, 19, 20, 21, 22, 23,
        8, 9, 10, 11, 12, 13, 14, 15,
        0, 1, 2, 3, 4, 5, 6, 7,
};

int getLineCount(FILE *fp){
    int count = 0;
    char c;
    for (c = getc(fp); c != EOF; c = getc(fp))
        if (c == '\n') // Increment count if this character is newline
            count = count + 1;
    fseek(fp, 0L, SEEK_SET);
    return count;
}

int32_t *features;
int32_t *labels;
int32_t linecount = -1;

char *data;

int32_t pieces[2][12][64];
int side;

int32_t char_pieces[] = {
        ['P'] = p_P + 1,
        ['N'] = p_N + 1,
        ['B'] = p_B + 1,
        ['R'] = p_R + 1,
        ['Q'] = p_Q + 1,
        ['K'] = p_K + 1,
        ['p'] = p_p + 1,
        ['n'] = p_n + 1,
        ['b'] = p_b + 1,
        ['r'] = p_r + 1,
        ['q'] = p_q + 1,
        ['k'] = p_k + 1
};

void parse_fen(char* fen){
    memset(pieces, 0, sizeof(pieces));

    int square = 0;
    for (int i = 0; i < 100; i++){
        char c = fen[i];
        if (c == ' '){
            assert(fen[i+1] == 'w' || fen[i+1] == 'b');
            if (fen[i+1] == 'w'){
                side = WHITE;
            } else {
                side == BLACK;
            }
            break;
        }
        if (c == '/')
            continue;

        if (char_pieces[c] == 0){
            square += atoi(&fen[i]);
        } else {
            pieces[0][char_pieces[c]-1][square] = 1;
            pieces[1][FLIP_PIECE[char_pieces[c]-1]][flip[square]] = 1;
            square++;
        }
    }
}

char piece_symbols[12] = {
        'P', 'N', 'B', 'R', 'Q', 'K', 'p', 'n', 'b', 'r', 'q', 'k'
};

void print_board(){
    int32_t rank = 8;
    for (int32_t square = 0; square < 64; square++){

        if (!(square % 8)) {
            printf("\n");
            printf("%d | ", rank);
            rank--;
        }

        int32_t found_piece = 0;

        for (int32_t piece = p_P; piece <= p_k; piece++){
            if (pieces[piece][square]){
                printf("%c ", piece_symbols[piece]);
                found_piece = 1;
                break;
            }
        }

        if (!found_piece)
            printf(". ");
    }
    printf("\n    _______________\n");
    printf("    A B C D E F G H\n\n");

    printf("side to move : %s", side? "white" : "black");

}

int strscan(char* str, char chr){
    for (int32_t i = 0; i < 256; i++) {
        if (str[i] == chr){
            return i;
        }
    }

    printf("CHAR NOT FOUND\n");
    exit(1);
}

void init(int val, int batchSize){
    BATCH_SIZE = batchSize;
    features = malloc(sizeof(int32_t) * FEATURE_COUNT * BATCH_SIZE);
    labels = malloc(sizeof(int32_t) * BATCH_SIZE);
    
    FILE *fin;
    if (val){
        fin = fopen("val_chessData.csv", "r");
    } else {
        fin = fopen("chessData.csv", "r");
    }
    
    int count = getLineCount(fin);
    linecount = count;

    int64_t lineIndex = 0;
    data = malloc(sizeof(char) * count * MAX_LINE_LENGTH);

    char c;
    int64_t cindex = 0;

    for (int i = 0; i < linecount; i++){
        char* fenptr = &data[((int64_t)lineIndex*(int64_t)MAX_LINE_LENGTH)];

        fread(fenptr, sizeof(char), 100, fin);
        int32_t len = strscan(fenptr, '\n');

        fenptr[len] = '\0';
        lineIndex++;

        fseek(fin, len - MAX_LINE_LENGTH + 1, SEEK_CUR);
    }

    fclose(fin);
}

void ksqs(int* w, int* b){
    for (int i = 0; i < 64; i++) {
        if (pieces[p_K][i])
            *w = i;

        if (pieces[p_k][i])
            *b = flip[i];
    }
    
}

int *generate_features(int index){
    for (int batch = 0; batch < BATCH_SIZE; batch++) {
        parse_fen(&data[((int64_t)index * (int64_t)BATCH_SIZE * (int64_t)MAX_LINE_LENGTH) + ((int64_t)batch * (int64_t)MAX_LINE_LENGTH)]);
        memcpy(&features[batch*FEATURE_COUNT], pieces, sizeof(pieces));
    }

    return features;
}

int *generate_labels(int index){
    for (int i = 0; i < BATCH_SIZE; i++) {
        char* fen = &data[((int64_t)index * (int64_t)BATCH_SIZE * (int64_t)MAX_LINE_LENGTH) + ((int64_t)i * (int64_t)MAX_LINE_LENGTH)];

        for (int ch = 0; ch < 100; ch++) {
            if (fen[ch] == ','){

                if (fen[ch+1] == '#'){
                    if (fen[ch+2] == '-')
                        labels[i] = -10000;
                    else
                        labels[i] = 10000;
                } else {
                    labels[i] = atoi(&fen[ch+1]);
                }

                break;
            }
        }
        
    }
    
    return labels;
}

#ifdef EXE
int main(){

    init(1, 128);

    // for (int i = 0; i < linecount; i++) {
    //     printf("%d\n", i);
    //     generate_features(i);
    // }

    generate_features(20);
    // generate_labels(323150);
    

    // parse_fen(data);
    // print_board();

    return 0;
}
#endif
